import pygame
import psycopg2
from psycopg2 import sql

class DatabaseRoom:
    def __init__(self, player):
        self.player = player
        self.connection = None
        self.connection_status = "Not connected"
        self.tables = []
        self.table_data = []
        self.column_names = []
        self.scroll_offset = 0
        self.error_message = None

        # UI State
        self.view_mode = "folders"  # "folders", "table_view", "edit_row", "create_row"
        self.current_table = None
        self.mouse_pos = (0, 0)
        self.selected_row_index = -1
        self.edit_form_data = {}
        self.show_delete_confirm = False
        self.delete_row_index = -1

        # Mouse state
        self._last_mouse_state = False

        # Database connection string
        self.db_url = "postgresql://neondb_owner:npg_Jf2LGdNayZ3D@ep-late-bird-ahh0qy4j-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

        # Connect to database
        self.connect_to_database()

    def connect_to_database(self):
        """Connect to the PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(self.db_url)
            self.connection_status = "Connected successfully!"
            self.load_tables()
        except Exception as e:
            self.connection_status = f"Connection failed"
            self.error_message = str(e)

    def load_tables(self):
        """Load list of tables from the database"""
        if not self.connection:
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            self.tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
        except Exception as e:
            self.error_message = f"Error loading tables: {str(e)}"

    def load_table_data(self, table_name):
        """Load data from a specific table"""
        if not self.connection:
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute(sql.SQL("SELECT * FROM {} LIMIT 1000").format(
                sql.Identifier(table_name)
            ))
            self.table_data = cursor.fetchall()
            self.column_names = [desc[0] for desc in cursor.description]
            cursor.close()
            self.scroll_offset = 0
        except Exception as e:
            self.error_message = f"Error loading table data: {str(e)}"
            self.table_data = []

    def insert_row(self, table_name, data):
        """Insert a new row into the table"""
        if not self.connection:
            return False

        try:
            cursor = self.connection.cursor()
            # Filter out None values (auto-increment fields like id)
            filtered_data = {k: v for k, v in data.items() if v is not None}

            if not filtered_data:
                self.error_message = "No data to insert"
                return False

            columns = list(filtered_data.keys())
            values = list(filtered_data.values())

            query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(table_name),
                sql.SQL(', ').join(map(sql.Identifier, columns)),
                sql.SQL(', ').join(sql.Placeholder() * len(values))
            )
            cursor.execute(query, values)
            self.connection.commit()
            cursor.close()
            self.error_message = None  # Clear any previous errors
            return True
        except Exception as e:
            self.error_message = f"Error inserting row: {str(e)}"
            self.connection.rollback()
            return False

    def update_row(self, table_name, old_row, new_data):
        """Update an existing row"""
        if not self.connection:
            return False

        try:
            cursor = self.connection.cursor()

            # Build SET clause
            set_items = []
            set_values = []
            for col, val in new_data.items():
                set_items.append(sql.SQL("{} = {}").format(sql.Identifier(col), sql.Placeholder()))
                set_values.append(val)

            # Build WHERE clause (match all columns of old row)
            where_items = []
            where_values = []
            for i, col in enumerate(self.column_names):
                where_items.append(sql.SQL("{} = {}").format(sql.Identifier(col), sql.Placeholder()))
                where_values.append(old_row[i])

            query = sql.SQL("UPDATE {} SET {} WHERE {}").format(
                sql.Identifier(table_name),
                sql.SQL(', ').join(set_items),
                sql.SQL(' AND ').join(where_items)
            )

            cursor.execute(query, set_values + where_values)
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            self.error_message = f"Error updating row: {str(e)}"
            self.connection.rollback()
            return False

    def delete_row(self, table_name, row):
        """Delete a row from the table"""
        if not self.connection:
            return False

        try:
            cursor = self.connection.cursor()

            # Build WHERE clause (match all columns)
            where_items = []
            where_values = []
            for i, col in enumerate(self.column_names):
                where_items.append(sql.SQL("{} = {}").format(sql.Identifier(col), sql.Placeholder()))
                where_values.append(row[i])

            query = sql.SQL("DELETE FROM {} WHERE {}").format(
                sql.Identifier(table_name),
                sql.SQL(' AND ').join(where_items)
            )

            cursor.execute(query, where_values)
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            self.error_message = f"Error deleting row: {str(e)}"
            self.connection.rollback()
            return False

    def update(self, dt):
        # No player movement needed

        # Get mouse position and buttons
        self.mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        # Handle mouse clicks
        if mouse_buttons[0] and not self._last_mouse_state:
            self.handle_click(self.mouse_pos)

        self._last_mouse_state = mouse_buttons[0]

        # Handle keyboard
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            if self.view_mode == "edit_row" or self.view_mode == "create_row":
                self.view_mode = "table_view"
                pygame.time.wait(200)
            elif self.view_mode == "table_view":
                self.view_mode = "folders"
                self.current_table = None
                pygame.time.wait(200)

    def handle_click(self, pos):
        """Handle mouse clicks"""
        # Delete confirmation takes priority
        if self.show_delete_confirm:
            self.handle_delete_confirm_click(pos)
        elif self.view_mode == "folders":
            self.handle_folders_click(pos)
        elif self.view_mode == "table_view":
            self.handle_table_view_click(pos)
        elif self.view_mode == "edit_row" or self.view_mode == "create_row":
            self.handle_edit_form_click(pos)

    def handle_folders_click(self, pos):
        """Handle clicks in folders view"""
        folder_rects = self.get_folder_rects()
        for i, rect in enumerate(folder_rects):
            if rect.collidepoint(pos) and i < len(self.tables):
                self.current_table = self.tables[i]
                self.load_table_data(self.current_table)
                self.view_mode = "table_view"
                break

        # Check exit button
        exit_button = pygame.Rect(1150, 20, 100, 35)
        if exit_button.collidepoint(pos):
            self.view_mode = "exit"

    def handle_table_view_click(self, pos):
        """Handle clicks in table view"""
        # Back button
        back_button = pygame.Rect(30, 20, 100, 35)
        if back_button.collidepoint(pos):
            self.view_mode = "folders"
            self.current_table = None
            return

        # New row button
        new_button = pygame.Rect(1050, 90, 200, 40)
        if new_button.collidepoint(pos):
            # Pre-fill with default values
            self.edit_form_data = {}
            for col in self.column_names:
                if 'id' in col.lower():
                    self.edit_form_data[col] = None  # Auto-increment
                elif 'name' in col.lower() or 'username' in col.lower() or 'title' in col.lower():
                    self.edit_form_data[col] = "New Item"
                elif 'email' in col.lower():
                    self.edit_form_data[col] = "new@example.com"
                elif 'price' in col.lower():
                    self.edit_form_data[col] = 0.00
                elif 'age' in col.lower() or 'stock' in col.lower() or 'priority' in col.lower():
                    self.edit_form_data[col] = 0
                elif 'description' in col.lower():
                    self.edit_form_data[col] = "Description"
                elif 'category' in col.lower():
                    self.edit_form_data[col] = "General"
                elif 'completed' in col.lower():
                    self.edit_form_data[col] = False
                else:
                    self.edit_form_data[col] = "value"
            self.view_mode = "create_row"
            return

        # Check row action buttons
        visible_rows = self.table_data[self.scroll_offset:self.scroll_offset + 12]
        for i, row in enumerate(visible_rows):
            y_pos = 185 + i * 35

            # Edit button
            edit_btn = pygame.Rect(1100, y_pos, 70, 28)
            if edit_btn.collidepoint(pos):
                self.selected_row_index = self.scroll_offset + i
                self.edit_form_data = {self.column_names[j]: row[j] for j in range(len(self.column_names))}
                self.view_mode = "edit_row"
                return

            # Delete button
            delete_btn = pygame.Rect(1180, y_pos, 70, 28)
            if delete_btn.collidepoint(pos):
                self.delete_row_index = self.scroll_offset + i
                self.show_delete_confirm = True
                return

        # Scroll buttons
        if len(self.table_data) > 12:
            scroll_up_btn = pygame.Rect(1230, 140, 30, 30)
            scroll_down_btn = pygame.Rect(1230, 600, 30, 30)

            if scroll_up_btn.collidepoint(pos) and self.scroll_offset > 0:
                self.scroll_offset -= 1
            elif scroll_down_btn.collidepoint(pos) and self.scroll_offset < len(self.table_data) - 12:
                self.scroll_offset += 1

    def handle_edit_form_click(self, pos):
        """Handle clicks in edit/create form"""
        # Cancel button
        cancel_btn = pygame.Rect(450, 600, 150, 40)
        if cancel_btn.collidepoint(pos):
            self.view_mode = "table_view"
            self.error_message = None  # Clear error
            return

        # Save button
        save_btn = pygame.Rect(620, 600, 150, 40)
        if save_btn.collidepoint(pos):
            success = False
            if self.view_mode == "create_row":
                success = self.insert_row(self.current_table, self.edit_form_data)
            else:  # edit_row
                old_row = self.table_data[self.selected_row_index]
                success = self.update_row(self.current_table, old_row, self.edit_form_data)

            if success:
                self.load_table_data(self.current_table)
                self.view_mode = "table_view"
            # If failed, stay on form to show error message
            return

        # Check input fields
        for i, col in enumerate(self.column_names):
            field_rect = pygame.Rect(300, 200 + i * 50, 600, 35)
            if field_rect.collidepoint(pos):
                # Simple text input - get keyboard input
                self.edit_active_field = col
                return

    def handle_delete_confirm_click(self, pos):
        """Handle clicks in delete confirmation dialog"""
        # Cancel button
        cancel_btn = pygame.Rect(450, 400, 150, 40)
        if cancel_btn.collidepoint(pos):
            self.show_delete_confirm = False
            return

        # Confirm delete button
        confirm_btn = pygame.Rect(620, 400, 150, 40)
        if confirm_btn.collidepoint(pos):
            row_to_delete = self.table_data[self.delete_row_index]
            if self.delete_row(self.current_table, row_to_delete):
                self.load_table_data(self.current_table)
            self.show_delete_confirm = False
            return

    def get_folder_rects(self):
        """Calculate positions for folder icons"""
        folder_rects = []
        start_x = 80
        start_y = 120
        folder_width = 140
        folder_height = 140
        columns = 7
        spacing_x = 20
        spacing_y = 20

        for i in range(len(self.tables)):
            col = i % columns
            row = i // columns
            x = start_x + col * (folder_width + spacing_x)
            y = start_y + row * (folder_height + spacing_y)
            folder_rects.append(pygame.Rect(x, y, folder_width, folder_height))

        return folder_rects

    def player_wants_exit(self):
        """Check if player wants to exit"""
        return self.view_mode == "exit"

    def draw(self, screen):
        # Fill with Google Drive background color
        screen.fill((248, 249, 250))

        if self.show_delete_confirm:
            # First draw the underlying view
            if self.view_mode == "table_view":
                self.draw_table_view(screen)
            # Then draw delete confirmation on top
            self.draw_delete_confirmation(screen)
        elif self.view_mode == "folders":
            self.draw_folders_view(screen)
        elif self.view_mode == "table_view":
            self.draw_table_view(screen)
        elif self.view_mode == "edit_row" or self.view_mode == "create_row":
            self.draw_edit_form(screen)

    def draw_folders_view(self, screen):
        """Draw Google Drive style folders view"""
        # Header bar
        header_rect = pygame.Rect(0, 0, 1280, 70)
        pygame.draw.rect(screen, (255, 255, 255), header_rect)
        pygame.draw.line(screen, (220, 220, 220), (0, 70), (1280, 70), 2)

        # Title
        font_title = pygame.font.Font(None, 42)
        title_text = font_title.render("Secret Database", True, (50, 50, 50))
        screen.blit(title_text, (30, 20))

        # Connection status
        font_small = pygame.font.Font(None, 18)
        status_color = (52, 168, 83) if "success" in self.connection_status.lower() else (234, 67, 53)
        pygame.draw.circle(screen, status_color, (980, 34), 6)
        status_text = font_small.render("Connected" if "success" in self.connection_status.lower() else "Offline", True, (100, 100, 100))
        screen.blit(status_text, (995, 28))

        # Exit button
        exit_btn = pygame.Rect(1150, 20, 100, 35)
        exit_hovered = exit_btn.collidepoint(self.mouse_pos)
        pygame.draw.rect(screen, (234, 67, 53) if exit_hovered else (220, 70, 70), exit_btn, border_radius=4)
        exit_text = font_small.render("Exit Room", True, (255, 255, 255))
        screen.blit(exit_text, (1165, 30))

        # Draw folder icons
        folder_rects = self.get_folder_rects()
        font_folder = pygame.font.Font(None, 18)

        for i, rect in enumerate(folder_rects):
            if i >= len(self.tables):
                break

            is_hovered = rect.collidepoint(self.mouse_pos)

            # Folder card
            card_color = (255, 255, 255) if not is_hovered else (245, 248, 250)
            pygame.draw.rect(screen, card_color, rect, border_radius=8)
            pygame.draw.rect(screen, (200, 220, 240) if is_hovered else (230, 230, 230), rect, 2 if is_hovered else 1, border_radius=8)

            # Folder icon
            folder_icon_rect = pygame.Rect(rect.x + 40, rect.y + 25, 60, 50)
            tab_points = [
                (folder_icon_rect.x, folder_icon_rect.y + 10),
                (folder_icon_rect.x + 20, folder_icon_rect.y + 10),
                (folder_icon_rect.x + 25, folder_icon_rect.y),
                (folder_icon_rect.x + 60, folder_icon_rect.y),
                (folder_icon_rect.x + 60, folder_icon_rect.y + 10)
            ]
            pygame.draw.polygon(screen, (66, 133, 244), tab_points)
            folder_body = pygame.Rect(folder_icon_rect.x, folder_icon_rect.y + 10, 60, 40)
            pygame.draw.rect(screen, (66, 133, 244), folder_body, border_radius=3)

            # Table name
            table_name = self.tables[i]
            if len(table_name) > 18:
                table_name = table_name[:15] + "..."
            name_text = font_folder.render(table_name, True, (50, 50, 50))
            name_x = rect.centerx - name_text.get_width() // 2
            screen.blit(name_text, (name_x, rect.y + 95))

            row_count_text = font_small.render("Table", True, (120, 120, 120))
            count_x = rect.centerx - row_count_text.get_width() // 2
            screen.blit(row_count_text, (count_x, rect.y + 115))

        # Instructions
        if self.tables:
            hint_text = font_small.render("Click on a table to view and edit data", True, (100, 100, 100))
            screen.blit(hint_text, (30, 680))

    def draw_table_view(self, screen):
        """Draw table data view with CRUD operations"""
        # Header bar
        header_rect = pygame.Rect(0, 0, 1280, 70)
        pygame.draw.rect(screen, (255, 255, 255), header_rect)
        pygame.draw.line(screen, (220, 220, 220), (0, 70), (1280, 70), 2)

        # Back button
        back_button = pygame.Rect(30, 20, 100, 35)
        back_hovered = back_button.collidepoint(self.mouse_pos)
        pygame.draw.rect(screen, (240, 240, 240) if back_hovered else (255, 255, 255), back_button, border_radius=4)
        pygame.draw.rect(screen, (200, 200, 200), back_button, 1, border_radius=4)
        font_button = pygame.font.Font(None, 22)
        back_text = font_button.render("← Back", True, (50, 50, 50))
        screen.blit(back_text, (45, 28))

        # Breadcrumb
        font_breadcrumb = pygame.font.Font(None, 24)
        breadcrumb = font_breadcrumb.render(f"Database / {self.current_table}", True, (100, 100, 100))
        screen.blit(breadcrumb, (150, 28))

        # New row button
        new_button = pygame.Rect(1050, 90, 200, 40)
        new_hovered = new_button.collidepoint(self.mouse_pos)
        pygame.draw.rect(screen, (52, 168, 83) if new_hovered else (66, 133, 244), new_button, border_radius=4)
        new_text = font_button.render("+ New Row", True, (255, 255, 255))
        screen.blit(new_text, (1105, 100))

        # Table container
        table_container = pygame.Rect(30, 140, 1220, 490)
        pygame.draw.rect(screen, (255, 255, 255), table_container, border_radius=8)
        pygame.draw.rect(screen, (230, 230, 230), table_container, 1, border_radius=8)

        # Column headers
        font_header = pygame.font.Font(None, 20)
        font_cell = pygame.font.Font(None, 18)
        font_btn = pygame.font.Font(None, 16)

        if self.column_names:
            # Header background
            header_bg = pygame.Rect(30, 140, 1050, 35)
            pygame.draw.rect(screen, (245, 245, 245), header_bg, border_top_left_radius=8)

            # Show up to 5 columns
            col_width = 1050 // min(len(self.column_names), 5)
            for i, col_name in enumerate(self.column_names[:5]):
                if len(col_name) > 15:
                    col_name = col_name[:12] + "..."
                header_text = font_header.render(col_name, True, (70, 70, 70))
                screen.blit(header_text, (40 + i * col_width, 150))

            # Actions header
            actions_text = font_header.render("Actions", True, (70, 70, 70))
            screen.blit(actions_text, (1100, 150))

            # Draw table rows
            if self.table_data:
                visible_rows = self.table_data[self.scroll_offset:self.scroll_offset + 12]
                row_height = 35

                for row_idx, row in enumerate(visible_rows):
                    y_pos = 185 + row_idx * row_height

                    # Alternating row background
                    if row_idx % 2 == 0:
                        row_bg = pygame.Rect(30, y_pos - 5, 1220, row_height)
                        pygame.draw.rect(screen, (250, 250, 250), row_bg)

                    # Draw cells
                    for col_idx, value in enumerate(row[:5]):
                        cell_text = str(value)
                        if len(cell_text) > 18:
                            cell_text = cell_text[:15] + "..."
                        cell_surface = font_cell.render(cell_text, True, (50, 50, 50))
                        screen.blit(cell_surface, (40 + col_idx * col_width, y_pos))

                    # Edit button
                    edit_btn = pygame.Rect(1100, y_pos, 70, 28)
                    edit_hovered = edit_btn.collidepoint(self.mouse_pos)
                    pygame.draw.rect(screen, (240, 240, 240) if edit_hovered else (255, 255, 255), edit_btn, border_radius=3)
                    pygame.draw.rect(screen, (200, 200, 200), edit_btn, 1, border_radius=3)
                    edit_text = font_btn.render("Edit", True, (66, 133, 244))
                    screen.blit(edit_text, (1115, y_pos + 6))

                    # Delete button
                    delete_btn = pygame.Rect(1180, y_pos, 70, 28)
                    delete_hovered = delete_btn.collidepoint(self.mouse_pos)
                    pygame.draw.rect(screen, (240, 240, 240) if delete_hovered else (255, 255, 255), delete_btn, border_radius=3)
                    pygame.draw.rect(screen, (200, 200, 200), delete_btn, 1, border_radius=3)
                    delete_text = font_btn.render("Delete", True, (234, 67, 53))
                    screen.blit(delete_text, (1190, y_pos + 6))

                # Scroll indicators
                if len(self.table_data) > 12:
                    font_small = pygame.font.Font(None, 18)
                    scroll_text = font_small.render(f"Showing {self.scroll_offset + 1}-{min(self.scroll_offset + 12, len(self.table_data))} of {len(self.table_data)} rows", True, (120, 120, 120))
                    screen.blit(scroll_text, (35, 650))

                    # Scroll buttons
                    scroll_up_btn = pygame.Rect(1230, 140, 30, 30)
                    scroll_down_btn = pygame.Rect(1230, 600, 30, 30)

                    up_color = (66, 133, 244) if self.scroll_offset > 0 else (200, 200, 200)
                    down_color = (66, 133, 244) if self.scroll_offset < len(self.table_data) - 12 else (200, 200, 200)

                    pygame.draw.rect(screen, up_color, scroll_up_btn, border_radius=3)
                    pygame.draw.rect(screen, down_color, scroll_down_btn, border_radius=3)

                    # Draw arrows
                    font_arrow = pygame.font.Font(None, 24)
                    up_arrow = font_arrow.render("▲", True, (255, 255, 255))
                    down_arrow = font_arrow.render("▼", True, (255, 255, 255))
                    screen.blit(up_arrow, (1236, 142))
                    screen.blit(down_arrow, (1236, 602))

    def draw_edit_form(self, screen):
        """Draw edit/create form"""
        # Semi-transparent overlay
        overlay = pygame.Surface((1280, 720))
        overlay.set_alpha(200)
        overlay.fill((50, 50, 50))
        screen.blit(overlay, (0, 0))

        # Form container
        form_rect = pygame.Rect(250, 100, 780, 570)
        pygame.draw.rect(screen, (255, 255, 255), form_rect, border_radius=8)

        # Title
        font_title = pygame.font.Font(None, 36)
        title = "Create New Row" if self.view_mode == "create_row" else "Edit Row"
        title_text = font_title.render(title, True, (50, 50, 50))
        screen.blit(title_text, (280, 130))

        # Form fields
        font_label = pygame.font.Font(None, 20)
        font_input = pygame.font.Font(None, 18)

        y_offset = 200
        for i, col in enumerate(self.column_names):
            if y_offset > 550:
                break

            # Label
            label_text = font_label.render(col, True, (70, 70, 70))
            screen.blit(label_text, (300, y_offset - 20))

            # Input field
            input_rect = pygame.Rect(300, y_offset, 600, 35)
            pygame.draw.rect(screen, (248, 249, 250), input_rect, border_radius=4)
            pygame.draw.rect(screen, (200, 200, 200), input_rect, 1, border_radius=4)

            # Value
            value = str(self.edit_form_data.get(col, ""))
            if len(value) > 60:
                value = value[:60] + "..."
            value_text = font_input.render(value, True, (50, 50, 50))
            screen.blit(value_text, (310, y_offset + 8))

            y_offset += 50

        # Note about editing
        font_small = pygame.font.Font(None, 16)
        note_text = font_small.render("Note: Values are pre-filled with defaults. Click Save to insert with these values.", True, (150, 150, 150))
        screen.blit(note_text, (280, 540))

        # Error message if any
        if self.error_message:
            error_text = font_small.render(f"Error: {self.error_message[:80]}", True, (234, 67, 53))
            screen.blit(error_text, (280, 565))

        # Buttons
        cancel_btn = pygame.Rect(450, 600, 150, 40)
        save_btn = pygame.Rect(620, 600, 150, 40)

        cancel_hovered = cancel_btn.collidepoint(self.mouse_pos)
        save_hovered = save_btn.collidepoint(self.mouse_pos)

        pygame.draw.rect(screen, (240, 240, 240) if cancel_hovered else (255, 255, 255), cancel_btn, border_radius=4)
        pygame.draw.rect(screen, (200, 200, 200), cancel_btn, 1, border_radius=4)

        pygame.draw.rect(screen, (52, 168, 83) if save_hovered else (66, 133, 244), save_btn, border_radius=4)

        font_button = pygame.font.Font(None, 22)
        cancel_text = font_button.render("Cancel", True, (50, 50, 50))
        save_text = font_button.render("Save", True, (255, 255, 255))
        screen.blit(cancel_text, (490, 610))
        screen.blit(save_text, (665, 610))

    def draw_delete_confirmation(self, screen):
        """Draw delete confirmation dialog"""
        # Semi-transparent overlay
        overlay = pygame.Surface((1280, 720))
        overlay.set_alpha(200)
        overlay.fill((50, 50, 50))
        screen.blit(overlay, (0, 0))

        # Dialog box
        dialog_rect = pygame.Rect(390, 250, 500, 200)
        pygame.draw.rect(screen, (255, 255, 255), dialog_rect, border_radius=8)

        # Title
        font_title = pygame.font.Font(None, 32)
        title_text = font_title.render("Delete Row?", True, (234, 67, 53))
        screen.blit(title_text, (420, 280))

        # Message
        font_msg = pygame.font.Font(None, 20)
        msg_text = font_msg.render("Are you sure you want to delete this row?", True, (70, 70, 70))
        screen.blit(msg_text, (420, 330))
        msg_text2 = font_msg.render("This action cannot be undone.", True, (150, 150, 150))
        screen.blit(msg_text2, (420, 355))

        # Buttons
        cancel_btn = pygame.Rect(450, 400, 150, 40)
        confirm_btn = pygame.Rect(620, 400, 150, 40)

        cancel_hovered = cancel_btn.collidepoint(self.mouse_pos)
        confirm_hovered = confirm_btn.collidepoint(self.mouse_pos)

        pygame.draw.rect(screen, (240, 240, 240) if cancel_hovered else (255, 255, 255), cancel_btn, border_radius=4)
        pygame.draw.rect(screen, (200, 200, 200), cancel_btn, 1, border_radius=4)

        pygame.draw.rect(screen, (200, 70, 70) if confirm_hovered else (234, 67, 53), confirm_btn, border_radius=4)

        font_button = pygame.font.Font(None, 22)
        cancel_text = font_button.render("Cancel", True, (50, 50, 50))
        confirm_text = font_button.render("Delete", True, (255, 255, 255))
        screen.blit(cancel_text, (490, 410))
        screen.blit(confirm_text, (660, 410))

    def __del__(self):
        """Clean up database connection"""
        if self.connection:
            self.connection.close()
