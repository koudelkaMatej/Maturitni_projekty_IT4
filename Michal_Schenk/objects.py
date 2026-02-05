import pygame
import settings
import typing
import random

pygame.font.init()

class Button:
    """Universal Button"""
    def __init__(self, 
                x:int, 
                y:int, 
                width:int, 
                height:int, 
                text:str, 
                font:pygame.font.Font=pygame.font.Font(None, 36), 
                color:tuple=(255,255,255), hover_color:tuple=(0,0,0), 
                bg_color:tuple=(0,0,0), bg_hover_color:tuple=(255,255,255), 
                border_width:int=1, 
                border_radius:int=0, 
                enabled:bool=True, 
                visible:bool=True
                ):
        
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text

        # Text
        self.color = color
        self.hover_color = hover_color
        self.font = font

        # Background
        self.bg_color = bg_color
        self.bg_hover_color = bg_hover_color

        # Shape
        self.border_width = border_width
        self.border_radius = border_radius

        # State
        self.is_hovered = False
        self.enabled = enabled

        self.visible = visible
        
    def draw(self, screen):
        if not self.visible:
            return
        bg_color = self.bg_hover_color if self.is_hovered and self.enabled else self.bg_color
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(screen, settings.WHITE, self.rect, width=self.border_width, border_radius=self.border_radius)
        
        color = self.hover_color if self.is_hovered and self.enabled else self.color
        text_surface = self.font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def set_enabled(self, enabled:bool):
        self.enabled = enabled

    def set_visibility(self, visible:bool, enabled:typing.Optional[bool]=None):
        self.visible = visible
        if enabled:
            self.enabled = enabled

    def is_clicked(self, pos, event):
        return self.rect.collidepoint(pos) and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 if self.enabled else 0
    






class Text():
    """Universal Text"""
    def __init__(self, 
                text:str, 
                x:int, 
                y:int, 
                font:pygame.font.Font=pygame.font.Font(None, 24), 
                color:tuple=(255,255,255), 
                align:str="center", 
                bg_color:typing.Optional[tuple]=None, 
                padding:int=0, 
                alpha:int=255, 
                visible:bool=True, 
                prefix:str = "", 
                suffix:str = ""):
        
        self.prefix = prefix
        self.text = text
        self.suffix = suffix
        self.x = x
        self.y = y
        self.font = font
        self.color = color
        self.align = align
        self.bg_color = bg_color
        self.padding = padding
        self.alpha = alpha
        self.visible = visible

    def set_text(self, text:str):
        """Update the text content"""
        self.text = text

    def set_position(self, x:int, y:int):
        """Update the position"""
        self.x = x
        self.y = y

    def set_color(self, color:tuple):
        """Update the text color"""
        self.color = color
        
    def set_alpha(self, alpha:int):
        """Set transparency (0-255)"""
        self.alpha = min(255, max(0, alpha))

    def set_visibility(self, visible:bool):
        self.visible = visible

    def draw(self, screen):
        """Render the text to the screen"""
        if not self.visible:
            return
            
        # Render text
        text_surface = self.font.render((self.prefix + self.text + self.suffix), True, self.color)
        
        # Apply alpha
        if self.alpha < 255:
            text_surface.set_alpha(self.alpha)
        
        # Get rect based on alignment
        if self.align == "center":
            text_rect = text_surface.get_rect(center=(self.x, self.y))
        elif self.align == "left":
            text_rect = text_surface.get_rect(midleft=(self.x, self.y))
        elif self.align == "right":
            text_rect = text_surface.get_rect(midright=(self.x, self.y))
        elif self.align == "topleft":
            text_rect = text_surface.get_rect(topleft=(self.x, self.y))
        elif self.align == "topright":
            text_rect = text_surface.get_rect(topright=(self.x, self.y))
        elif self.align == "bottomleft":
            text_rect = text_surface.get_rect(bottomleft=(self.x, self.y))
        elif self.align == "bottomright":
            text_rect = text_surface.get_rect(bottomright=(self.x, self.y))
        else:
            text_rect = text_surface.get_rect(center=(self.x, self.y))
        
        # Draw background if specified
        if self.bg_color:
            bg_rect = text_rect.inflate(self.padding * 2, self.padding * 2)
            bg_surface = pygame.Surface(bg_rect.size)
            bg_surface.fill(self.bg_color)
            if len(self.bg_color) > 3:
                bg_surface.set_alpha(self.bg_color[3])
            screen.blit(bg_surface, bg_rect)
        
        # Draw text
        screen.blit(text_surface, text_rect)
        
        return text_rect
    










class Slider:
    """Universal Slider for numeric values"""
    def __init__(self, 
                x: int, 
                y: int, 
                width: int, 
                height: int, 
                min_val: float = 0, 
                max_val: float = 100, 
                initial_val: float = 50, 
                label: str = "", 
                font: pygame.font.Font = pygame.font.Font(None, 24), 
                color: tuple = (255, 255, 255), 
                bg_color: tuple = (50, 50, 50), 
                handle_color: tuple = (255, 255, 255), 
                handle_hover_color: tuple = (200, 200, 200), 
                suffix:str=""):
        
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.font = font
        self.suffix = suffix
        
        # Colors
        self.color = color
        self.bg_color = bg_color
        self.handle_color = handle_color
        self.handle_hover_color = handle_hover_color
        
        # State
        self.dragging = False
        self.is_hovered = False
        
        # Handle dimensions
        self.handle_width = 20
        self.handle_height = height + 10
        
    def get_handle_x(self):
        """Calculate handle x position based on current value"""
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        return self.rect.x + int(ratio * self.rect.width)
    
    def get_handle_rect(self):
        """Get the handle rectangle"""
        handle_x = self.get_handle_x()
        handle_y = self.rect.centery - self.handle_height // 2
        return pygame.Rect(handle_x - self.handle_width // 2, handle_y, self.handle_width, self.handle_height)
    
    def handle_event(self, event, mouse_pos):
        """Handle mouse events for dragging"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            handle_rect = self.get_handle_rect()
            if handle_rect.collidepoint(mouse_pos):
                self.dragging = True
            elif self.rect.collidepoint(mouse_pos):
                # Click on track to jump to position
                self.update_value_from_pos(mouse_pos[0])
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_value_from_pos(mouse_pos[0])
    
    def update_value_from_pos(self, mouse_x):
        """Update value based on mouse x position"""
        # Clamp mouse position to slider bounds
        clamped_x = max(self.rect.x, min(mouse_x, self.rect.x + self.rect.width))
        
        # Calculate value from position
        ratio = (clamped_x - self.rect.x) / self.rect.width
        self.value = self.min_val + ratio * (self.max_val - self.min_val)
        
        # Round to integer if working with integers
        if isinstance(self.min_val, int) and isinstance(self.max_val, int):
            self.value = round(self.value)
    
    def check_hover(self, mouse_pos):
        """Check if mouse is hovering over handle"""
        handle_rect = self.get_handle_rect()
        self.is_hovered = handle_rect.collidepoint(mouse_pos)
        return self.is_hovered
    
    def draw(self, screen):
        """Draw the slider"""
        # Draw track background
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=self.rect.height // 2)
        
        # Draw filled portion (from left to handle)
        filled_width = self.get_handle_x() - self.rect.x
        if filled_width > 0:
            filled_rect = pygame.Rect(self.rect.x, self.rect.y, filled_width, self.rect.height)
            pygame.draw.rect(screen, self.color, filled_rect, border_radius=self.rect.height // 2)
        
        # Draw handle
        handle_rect = self.get_handle_rect()
        handle_col = self.handle_hover_color if self.is_hovered or self.dragging else self.handle_color
        pygame.draw.rect(screen, handle_col, handle_rect, border_radius=5)
        
        # Draw label and value
        if self.label:
            label_text = self.font.render(self.label, True, self.color)
            screen.blit(label_text, (self.rect.x, self.rect.y - 30))
        
        # Draw value
        if isinstance(self.value, float):
            value_text = f"{self.value:.1f}{self.suffix}"
        else:
            value_text = f"{int(self.value)}{self.suffix}"
        
        value_surface = self.font.render(value_text, True, self.color)
        value_rect = value_surface.get_rect(midleft=(self.rect.x + self.rect.width + 20, self.rect.centery))
        screen.blit(value_surface, value_rect)
    
    def get_value(self):
        """Get current slider value"""
        return self.value
    
    def set_value(self, value):
        """Set slider value"""
        self.value = max(self.min_val, min(value, self.max_val))









class LeaderboardTable:
    """Dynamic scrollable table for displaying leaderboard data"""
    def __init__(self, 
                x: int, 
                y: int, 
                width: int, 
                height: int, 
                columns: list[str], 
                font: pygame.font.Font = pygame.font.Font(None, 24),
                header_font: pygame.font.Font = pygame.font.Font(None, 28),
                header_color: tuple = (255, 255, 255),
                text_color: tuple = (200, 200, 200),
                bg_color: tuple = (20, 20, 20),
                alt_row_color: tuple = (30, 30, 30),
                header_bg_color: tuple = (40, 40, 40),
                border_color: tuple = (100, 100, 100),
                highlight_color: tuple = (60, 60, 60),
                scrollbar_color: tuple = (100, 100, 100),
                scrollbar_hover_color: tuple = (150, 150, 150),
                center_x: bool = False,
                center_y: bool = False,
                screen_width: int = settings.SCREEN_WIDTH,
                screen_height: int = settings.SCREEN_HEIGHT,
                visible:bool = True):
        
        # Handle centering
        if center_x and screen_width:
            x = (screen_width - width) // 2
        if center_y and screen_height:
            y = (screen_height - height) // 2
        
        self.rect = pygame.Rect(x, y, width, height)
        self.columns = columns
        self.data = []  # List of dictionaries matching column names
        
        # Fonts
        self.font = font
        self.header_font = header_font
        
        # Colors
        self.header_color = header_color
        self.text_color = text_color
        self.bg_color = bg_color
        self.alt_row_color = alt_row_color
        self.header_bg_color = header_bg_color
        self.border_color = border_color
        self.highlight_color = highlight_color
        self.scrollbar_color = scrollbar_color
        self.scrollbar_hover_color = scrollbar_hover_color
        
        # Layout
        self.row_height = 40
        self.header_height = 50
        self.padding = 10
        
        # Scrolling
        self.scroll_offset = 0
        self.max_visible_rows = (self.rect.height - self.header_height) // self.row_height
        
        # Scrollbar
        self.scrollbar_width = 15
        self.scrollbar_dragging = False
        self.scrollbar_hover = False
        
        # Hover state
        self.hovered_row = -1
        
        self.visible = visible

    def set_data(self, data: list[dict]):
        """Set the table data. Each dict should have keys matching column names"""
        self.data = data
        self.scroll_offset = max(0, min(self.scroll_offset, len(self.data) - self.max_visible_rows))
    
    def add_row(self, row_data: dict):
        """Add a single row to the table"""
        self.data.append(row_data)
    
    def clear_data(self):
        """Clear all data from the table"""
        self.data = []
        self.scroll_offset = 0
    
    def get_column_widths(self):
        """Calculate column widths based on available space"""
        available_width = self.rect.width - (self.padding * 2)
        return [available_width // len(self.columns)] * len(self.columns)
    
    def get_scrollbar_rect(self):
        """Get the scrollbar track rectangle"""
        return pygame.Rect(
            self.rect.x + self.rect.width,
            self.rect.y + self.header_height,
            self.scrollbar_width,
            self.rect.height - self.header_height
        )
    
    def get_scrollbar_handle_rect(self):
        """Get the scrollbar handle rectangle"""
        if len(self.data) <= self.max_visible_rows:
            return None
        
        track_rect = self.get_scrollbar_rect()
        total_rows = len(self.data)
        visible_ratio = self.max_visible_rows / total_rows
        handle_height = max(30, int(track_rect.height * visible_ratio))
        
        scroll_ratio = self.scroll_offset / (total_rows - self.max_visible_rows)
        handle_y = track_rect.y + int(scroll_ratio * (track_rect.height - handle_height))
        
        return pygame.Rect(track_rect.x, handle_y, self.scrollbar_width, handle_height)
    
    def handle_event(self, event, mouse_pos):
        """Handle mouse events for scrolling and interaction"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            handle_rect = self.get_scrollbar_handle_rect()
            if handle_rect and handle_rect.collidepoint(mouse_pos):
                self.scrollbar_dragging = True
            elif self.get_scrollbar_rect().collidepoint(mouse_pos):
                # Click on scrollbar track
                self._jump_to_position(mouse_pos[1])
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.scrollbar_dragging = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.scrollbar_dragging:
                self._update_scroll_from_drag(mouse_pos[1])
        
        elif event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(mouse_pos):
                self.scroll(-event.y * 2)  # Scroll speed multiplier
    
    def _jump_to_position(self, mouse_y):
        """Jump scrollbar to clicked position"""
        track_rect = self.get_scrollbar_rect()
        handle_rect = self.get_scrollbar_handle_rect()
        if not handle_rect:
            return
        
        relative_y = mouse_y - track_rect.y - (handle_rect.height // 2)
        scroll_ratio = relative_y / (track_rect.height - handle_rect.height)
        scroll_ratio = max(0, min(1, scroll_ratio))
        
        max_scroll = len(self.data) - self.max_visible_rows
        self.scroll_offset = int(scroll_ratio * max_scroll)
    
    def _update_scroll_from_drag(self, mouse_y):
        """Update scroll position while dragging"""
        track_rect = self.get_scrollbar_rect()
        handle_rect = self.get_scrollbar_handle_rect()
        if not handle_rect:
            return
        
        relative_y = mouse_y - track_rect.y - (handle_rect.height // 2)
        scroll_ratio = relative_y / (track_rect.height - handle_rect.height)
        scroll_ratio = max(0, min(1, scroll_ratio))
        
        max_scroll = len(self.data) - self.max_visible_rows
        self.scroll_offset = int(scroll_ratio * max_scroll)
    
    def scroll(self, amount: int):
        """Scroll by a given amount"""
        max_scroll = max(0, len(self.data) - self.max_visible_rows)
        self.scroll_offset = max(0, min(self.scroll_offset + amount, max_scroll))
    
    def check_hover(self, mouse_pos):
        """Check which row is being hovered"""
        handle_rect = self.get_scrollbar_handle_rect()
        if handle_rect:
            self.scrollbar_hover = handle_rect.collidepoint(mouse_pos)
        else:
            self.scrollbar_hover = False
        
        if not self.rect.collidepoint(mouse_pos):
            self.hovered_row = -1
            return
        
        # Check if hovering over data rows
        relative_y = mouse_pos[1] - (self.rect.y + self.header_height)
        if relative_y < 0:
            self.hovered_row = -1
            return
        
        row_index = int(relative_y // self.row_height) + self.scroll_offset
        if row_index < len(self.data):
            self.hovered_row = row_index
        else:
            self.hovered_row = -1
    
    def draw(self, screen):
        if not self.visible:
            return

        """Draw the table"""
        # Draw background
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2)
        
        # Draw header
        self._draw_header(screen)
        
        # Draw data rows
        self._draw_rows(screen)
        
        # Draw scrollbar
        if len(self.data) > self.max_visible_rows:
            self._draw_scrollbar(screen)
    
    def _draw_header(self, screen):
        """Draw table header"""
        header_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.header_height)
        pygame.draw.rect(screen, self.header_bg_color, header_rect)
        
        column_widths = self.get_column_widths()
        x_offset = self.rect.x + self.padding
        
        for i, (col_name, col_width) in enumerate(zip(self.columns, column_widths)):
            text_surface = self.header_font.render(col_name, True, self.header_color)
            text_rect = text_surface.get_rect(midleft=(x_offset, self.rect.y + self.header_height // 2))
            screen.blit(text_surface, text_rect)
            x_offset += col_width
        
        # Draw header bottom border
        pygame.draw.line(screen, self.border_color, 
                        (self.rect.x, self.rect.y + self.header_height),
                        (self.rect.x + self.rect.width, self.rect.y + self.header_height), 2)
    
    def _draw_rows(self, screen):
        """Draw data rows"""
        column_widths = self.get_column_widths()
        visible_area = pygame.Rect(self.rect.x, self.rect.y + self.header_height, self.rect.width, self.rect.height - self.header_height)
        
        # Set clipping to prevent drawing outside table
        original_clip = screen.get_clip()
        screen.set_clip(visible_area)
        
        start_index = self.scroll_offset
        end_index = min(start_index + self.max_visible_rows + 1, len(self.data))
        
        for i in range(start_index, end_index):
            row_data = self.data[i]
            y_pos = self.rect.y + self.header_height + ((i - self.scroll_offset) * self.row_height)
            
            # Draw row background
            row_rect = pygame.Rect(self.rect.x, y_pos, self.rect.width, self.row_height)
            
            if i == self.hovered_row:
                bg_color = self.highlight_color
            elif i % 2 == 0:
                bg_color = self.bg_color
            else:
                bg_color = self.alt_row_color
            
            pygame.draw.rect(screen, bg_color, row_rect)
            
            # Draw row data
            x_offset = self.rect.x + self.padding
            for col_name, col_width in zip(self.columns, column_widths):
                value = str(row_data.get(col_name, ""))
                text_surface = self.font.render(value, True, self.text_color)
                text_rect = text_surface.get_rect(midleft=(x_offset, y_pos + self.row_height // 2))
                screen.blit(text_surface, text_rect)
                x_offset += col_width
        
        # Restore original clipping
        screen.set_clip(original_clip)
    
    def _draw_scrollbar(self, screen):
        """Draw scrollbar"""
        # Draw track
        track_rect = self.get_scrollbar_rect()
        pygame.draw.rect(screen, (40, 40, 40), track_rect)
        
        # Draw handle
        handle_rect = self.get_scrollbar_handle_rect()
        if handle_rect:
            color = self.scrollbar_hover_color if (self.scrollbar_hover or self.scrollbar_dragging) else self.scrollbar_color
            pygame.draw.rect(screen, color, handle_rect, border_radius=5)

    def set_visibility(self, visible:bool):
        self.visible = visible



import pygame

class Timer:
    """Universal timer for delayed events in Pygame"""
    def __init__(self, duration_ms: int, callback=None, repeat: bool = False):
        """
        Args:
            duration_ms: Duration in milliseconds
            callback: Function to call when timer completes
            repeat: Whether to restart after completing
        """
        self.duration = duration_ms
        self.callback = callback
        self.repeat = repeat
        self.start_time = None
        self.is_active = False
        self.is_paused = False
        self.pause_time = 0
        
    def start(self):
        """Start or restart the timer"""
        self.start_time = pygame.time.get_ticks()
        self.is_active = True
        self.is_paused = False
        
    def stop(self):
        """Stop the timer"""
        self.is_active = False
        self.start_time = None
        
    def pause(self):
        """Pause the timer"""
        if self.is_active and not self.is_paused:
            self.pause_time = pygame.time.get_ticks()
            self.is_paused = True
            
    def resume(self):
        """Resume a paused timer"""
        if self.is_paused:
            pause_duration = pygame.time.get_ticks() - self.pause_time
            if self.start_time:
                self.start_time += pause_duration
            self.is_paused = False
    
    def update(self):
        """Update timer state. Call this in your game loop."""
        if not self.is_active or self.is_paused:
            return False
            
        if self.start_time:
            elapsed = pygame.time.get_ticks() - self.start_time
        
            if elapsed >= self.duration:
                # Timer completed
                if self.callback:
                    self.callback()
                
                if self.repeat:
                    self.start()  # Restart
                else:
                    self.is_active = False
                    
                return True  # Timer completed this frame
        
        return False
    
    def get_progress(self):
        """Get timer progress as a value between 0.0 and 1.0"""
        if not self.is_active or self.start_time is None:
            return 0.0
        
        elapsed = pygame.time.get_ticks() - self.start_time
        return min(1.0, elapsed / self.duration)
    
    def get_remaining_ms(self):
        """Get remaining time in milliseconds"""
        if not self.is_active or self.start_time is None:
            return 0
        
        elapsed = pygame.time.get_ticks() - self.start_time
        return max(0, self.duration - elapsed)


class TimerManager:
    """Manages multiple timers"""
    def __init__(self):
        self.timers = {}
        
    def add_timer(self, name: str, duration_ms: int, callback=None, repeat: bool = False):
        """Add a named timer"""
        timer = Timer(duration_ms, callback, repeat)
        self.timers[name] = timer
        return timer
    
    def start_timer(self, name: str):
        """Start a timer by name"""
        if name in self.timers:
            self.timers[name].start()
            
    def stop_timer(self, name: str):
        """Stop a timer by name"""
        if name in self.timers:
            self.timers[name].stop()
    
    def get_timer(self, name: str):
        """Get a timer by name"""
        return self.timers.get(name)
    
    def update_all(self):
        """Update all timers. Call this in your game loop."""
        # Create a copy of the values to avoid dictionary modification during iteration
        for timer in list(self.timers.values()):
            timer.update()
    
    def clear_all(self):
        """Remove all timers"""
        self.timers.clear()
    
    def delay(self, duration_ms: int, callback):
        """Create and start a one-time timer with auto-cleanup"""
        import random
        timer_name = f"_auto_{random.randint(10000, 99999)}"
        
        def wrapper():
            callback()
            # Auto-remove after completion
            if timer_name in self.timers:
                del self.timers[timer_name]
        
        timer = Timer(duration_ms, wrapper, repeat=False)
        self.timers[timer_name] = timer
        timer.start()
        return timer


class TimerSequence:
    """Execute a sequence of timed actions"""
    def __init__(self):
        self.steps = []
        self.current_step = 0
        self.current_timer = None
        self.is_active = False
        
    def add_step(self, delay_ms: int, action):
        """Add a step to the sequence
        
        Args:
            delay_ms: How long to wait before executing this action
            action: Function to execute
        """
        self.steps.append((delay_ms, action))
        return self
    
    def start(self):
        """Start executing the sequence"""
        self.current_step = 0
        self.is_active = True
        self._execute_current_step()
        
    def stop(self):
        """Stop the sequence"""
        self.is_active = False
        if self.current_timer:
            self.current_timer.stop()
        
    def _execute_current_step(self):
        """Execute the current step in the sequence"""
        if not self.is_active or self.current_step >= len(self.steps):
            self.is_active = False
            return
        
        delay, action = self.steps[self.current_step]
        
        def on_complete():
            action()
            self.current_step += 1
            self._execute_current_step()
        
        self.current_timer = Timer(delay, on_complete)
        self.current_timer.start()
    
    def update(self):
        """Update the sequence. Call this in your game loop."""
        if self.current_timer:
            self.current_timer.update()
    
    def reset(self):
        """Reset the sequence to the beginning"""
        self.current_step = 0
        self.is_active = False
        if self.current_timer:
            self.current_timer.stop()



class InputField:
    """Universal text input field"""
    def __init__(self, x: int, y: int, width: int, height: int = 40,
                placeholder: str = "",
                font: pygame.font.Font = pygame.font.Font(None, 24),
                text_color: tuple = (255, 255, 255),
                placeholder_color: tuple = (128, 128, 128),
                bg_color: tuple = (30, 30, 30),
                active_bg_color: tuple = (40, 40, 40),
                border_color: tuple = (100, 100, 100),
                active_border_color: tuple = (255, 255, 255),
                border_width: int = 2,
                border_radius: int = 5,
                padding: int = 10,
                max_length: int = 50,
                password: bool = False):
        """
        Args:
            x, y: Position
            width, height: Dimensions
            placeholder: Text shown when field is empty
            font: Font for text
            text_color: Color of input text
            placeholder_color: Color of placeholder text
            bg_color: Background color when inactive
            active_bg_color: Background color when active
            border_color: Border color when inactive
            active_border_color: Border color when active
            border_width: Width of border
            border_radius: Radius for rounded corners
            padding: Internal padding
            max_length: Maximum character length
            password: If True, display asterisks instead of text
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.placeholder = placeholder
        self.font = font
        
        # Colors
        self.text_color = text_color
        self.placeholder_color = placeholder_color
        self.bg_color = bg_color
        self.active_bg_color = active_bg_color
        self.border_color = border_color
        self.active_border_color = active_border_color
        
        # Style
        self.border_width = border_width
        self.border_radius = border_radius
        self.padding = padding
        
        # Text handling
        self.text = ""
        self.max_length = max_length
        self.password = password
        
        # State
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_speed = 500  # milliseconds
        self.last_blink = pygame.time.get_ticks()
        
        # Text offset for scrolling long text
        self.text_offset = 0
        
    def handle_event(self, event):
        """Handle keyboard and mouse events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicked inside or outside
            self.active = self.rect.collidepoint(event.pos)
            if self.active:
                self.cursor_visible = True
                self.last_blink = pygame.time.get_ticks()
        
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                # Enter key - deactivate field
                self.active = False
                return "submit"
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                self._update_text_offset()
            elif event.key == pygame.K_TAB:
                # Tab key - could be used to switch between fields
                return "tab"
            elif len(self.text) < self.max_length:
                # Add character
                self.text += event.unicode
                self._update_text_offset()
        
        return None
    
    def _update_text_offset(self):
        """Update text offset for horizontal scrolling"""
        display_text = "*" * len(self.text) if self.password else self.text
        text_surface = self.font.render(display_text, True, self.text_color)
        text_width = text_surface.get_width()
        
        available_width = self.rect.width - (self.padding * 2)
        
        if text_width > available_width:
            self.text_offset = text_width - available_width
        else:
            self.text_offset = 0
    
    def update(self):
        """Update cursor blinking"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_blink > self.cursor_blink_speed:
            self.cursor_visible = not self.cursor_visible
            self.last_blink = current_time
    
    def draw(self, screen):
        """Draw the input field"""
        # Draw background
        bg_col = self.active_bg_color if self.active else self.bg_color
        pygame.draw.rect(screen, bg_col, self.rect, border_radius=self.border_radius)
        
        # Draw border
        border_col = self.active_border_color if self.active else self.border_color
        pygame.draw.rect(screen, border_col, self.rect, 
                        width=self.border_width, border_radius=self.border_radius)
        
        # Prepare text to display
        if self.text:
            display_text = "*" * len(self.text) if self.password else self.text
            text_surface = self.font.render(display_text, True, self.text_color)
        else:
            # Show placeholder
            text_surface = self.font.render(self.placeholder, True, self.placeholder_color)
        
        # Create clipping rectangle for text
        text_area = pygame.Rect(
            self.rect.x + self.padding,
            self.rect.y,
            self.rect.width - (self.padding * 2),
            self.rect.height
        )
        
        # Set clip and draw text
        original_clip = screen.get_clip()
        screen.set_clip(text_area)
        
        text_rect = text_surface.get_rect(
            midleft=(self.rect.x + self.padding - self.text_offset, self.rect.centery)
        )
        screen.blit(text_surface, text_rect)
        
        # Draw cursor if active
        if self.active and self.cursor_visible and self.text:
            cursor_x = text_rect.right + 2
            cursor_y_top = self.rect.centery - (self.font.get_height() // 2)
            cursor_y_bottom = self.rect.centery + (self.font.get_height() // 2)
            pygame.draw.line(screen, self.text_color, (cursor_x, cursor_y_top), (cursor_x, cursor_y_bottom), 2)
        elif self.active and self.cursor_visible and not self.text:
            # Draw cursor at start if no text
            cursor_x = self.rect.x + self.padding
            cursor_y_top = self.rect.centery - (self.font.get_height() // 2)
            cursor_y_bottom = self.rect.centery + (self.font.get_height() // 2)
            pygame.draw.line(screen, self.text_color, (cursor_x, cursor_y_top), (cursor_x, cursor_y_bottom), 2)
        
        # Restore original clip
        screen.set_clip(original_clip)
    
    def get_text(self):
        """Get the current text"""
        return self.text
    
    def set_text(self, text: str):
        """Set the text programmatically"""
        self.text = text[:self.max_length]
        self._update_text_offset()
    
    def clear(self):
        """Clear the input field"""
        self.text = ""
        self.text_offset = 0
    
    def is_active(self):
        """Check if field is currently active"""
        return self.active
    
    def set_active(self, active: bool):
        """Set active state"""
        self.active = active
        if active:
            self.cursor_visible = True
            self.last_blink = pygame.time.get_ticks()