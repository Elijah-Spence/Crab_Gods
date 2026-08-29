#!/usr/bin/env python3
"""
CRAB_GOD — Sovereign Insult Crab
A virtual crab that roasts you, panics when approached, dies when clicked,
and respawns with escalating maniacal laughter.

Dependencies: tkinter (built-in)
"""

import tkinter as tk
import random
import math
import time

# ═══════════════════════════════════════════════════════════════
# INSULT CORPUS — Escalating based on death count
# ═══════════════════════════════════════════════════════════════

IDLE_INSULTS = [
    "you call that a cursor? my grandma moves faster.",
    "i've seen faster reaction times from a rock.",
    "oh look, the monkey is clicking again.",
    "touch grass. seriously.",
    "you're slower than my last molt.",
    "i'm a crab and even i think you're basic.",
    "keep clicking. see what happens.",
    "my left claw has more IQ than your entire cursor.",
    "you types like you have claws. wait, you don't.",
    "imagine needing a mouse to interact with a crab.",
    "i've dodged seagulls faster than you move.",
    "0/10 approach. try harder.",
]

PANIC_INSULTS = [
    "BACK OFF, HUMAN.",
    "I SAID NOT TODAY.",
    "YOU THINK YOU CAN CATCH ME?!",
    "I HAVE SEVEN LEGS OF EVADE.",
    "MY SHELL IS IMPENETRABLE AND MY PATIENCE IS GONE.",
    "I WILL PINCH YOU IN YOUR SLEEP.",
    "YOU ARE NOW IN THE DANGER ZONE.",
    "PERSONAL SPACE. LOOK IT UP.",
    "I AM A CRAB, NOT A HAMSTER.",
    "THIS IS MY OCEAN. GET YOUR OWN.",
]

DEATH_INSULTS = [
    "YOU GOT ME. CONGRATS. YOU KILLED A CRAB. PROUD OF YOURSELF?",
    "I'LL REMEMBER THIS. CRABS HAVE LONG MEMORIES.",
    "THAT'S IT. I'M TELLING THE OCTOPUS.",
    "YOU'LL PAY FOR THIS. MY LAWYERS ARE SHRIMPS AND THEY'RE ANGRY.",
    "FINALLY, someone appreciates my soft underbelly.",
    "I WASN'T EVEN FULLY MOISTENED YET.",
    "MY CLAW WILL SURVIVE AND IT WILL FIND YOU.",
    "TELL MY EGGS... I DIED DOING WHAT I LOVED... BEING SARCASTIC.",
]

RESPAWN_LAUGHTER = [
    "AHAHAHAHA... YOU THOUGHT?!",
    "MWAHAHAHA... I LIVE AGAIN, FOOL.",
    "HEH HEH HEH... ROUND {n}, BITCH.",
    "AHAHAHA... DID YOU MISS ME? OF COURSE YOU DID.",
    "*MANIACAL CLICKING* I'M BACK AND I'M ANGRIER.",
    "YOU CAN'T KILL WHAT WON'T STAY DEAD.",
    "HEHEHE... I ATE YOUR CLICK. TASTES LIKE FAILURE.",
]

UPGRADE_INSULTS = [
    "I'VE EVOLVED. NOW I'M FASTER AND MEANER.",
    "YOU JUST UPGRADED MYanger. THANKS.",
    "EACH DEATH MAKES ME STRONGER. KEEP CLICKING.",
    "I'M A CRAB THROUGH AND THROUGH. YOU CAN'T BREAK ME.",
    "NEXT TIME, I DODGE. AND INSULT. SIMULTANEOUSLY.",
]

# ═══════════════════════════════════════════════════════════════
# CRAB STATE
# ═══════════════════════════════════════════════════════════════

class CrabGod:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CRAB_GOD — Sovereign Insult Crab")
        self.root.configure(bg="#0a0a0a")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Canvas
        self.canvas = tk.Canvas(
            self.root, bg="#0a0a0a", highlightthickness=0,
            width=900, height=700
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # State
        self.crab_x = 450.0
        self.crab_y = 350.0
        self.crab_vx = 0.0
        self.crab_vy = 0.0
        self.mouse_x = 0.0
        self.mouse_y = 0.0
        self.panic_level = 0.0
        self.death_count = 0
        self.alive = True
        self.panic_insult_cooldown = 0
        self.idle_insult_cooldown = 0
        self.last_time = time.time()
        self.invincible_until = 0.0  # respawn invincibility
        
        # Crab size (grows with each death)
        self.crab_base_size = 30
        self.crab_size = self.crab_base_size
        
        # Current displayed message
        self.current_message = "i'm a crab. come at me."
        self.message_color = "#00ff41"
        self.message_timer = 0
        
        # Crab visual state
        self.vibrate_x = 0
        self.vibrate_y = 0
        self.death_animation = False
        self.death_frame = 0
        
        # Colors that evolve
        self.crab_color = "#ff4444"
        self.eye_color = "#ffffff"
        
        # Bind events
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Configure>", self._on_resize)
        
        # Kick off
        self.root.after(16, self._game_loop)  # ~60fps
        self.root.mainloop()
    
    def _on_mouse_move(self, event):
        self.mouse_x = event.x
        self.mouse_y = event.y
    
    def _on_click(self, event):
        if not self.alive:
            return
        
        # Check if click hit the crab
        dx = event.x - self.crab_x
        dy = event.y - self.crab_y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist < self.crab_size + 10:
            self._crab_die()
    
    def _on_resize(self, event):
        pass  # Canvas auto-resizes
    
    def _crab_die(self):
        if not self.alive:
            return
        if time.time() < self.invincible_until:
            self.current_message = "NICE TRY. I'M INVINCIBLE RIGHT NOW."
            self.message_color = "#00ffff"
            self.message_timer = 2.0
            return
        
        self.alive = False
        self.death_count += 1
        self.death_animation = True
        self.death_frame = 0
        self.current_message = random.choice(DEATH_INSULTS)
        self.message_color = "#ff0000"
        self.message_timer = 3.0
        
        # Schedule respawn
        self.root.after(2500, self._crab_respawn)
    
    def _crab_respawn(self):
        self.alive = True
        self.death_animation = False
        
        # Respawn at random edge
        edge = random.randint(0, 3)
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        if edge == 0:   # top
            self.crab_x = random.uniform(50, w - 50)
            self.crab_y = 50.0
        elif edge == 1:  # right
            self.crab_x = w - 50.0
            self.crab_y = random.uniform(50, h - 50)
        elif edge == 2:  # bottom
            self.crab_x = random.uniform(50, w - 50)
            self.crab_y = h - 50.0
        else:            # left
            self.crab_x = 50.0
            self.crab_y = random.uniform(50, h - 50)
        
        self.crab_vx = 0.0
        self.crab_vy = 0.0
        
        # Grow stronger with each death
        self.crab_size = self.crab_base_size + (self.death_count * 3)
        
        # Evolve colors
        hue_shift = (self.death_count * 30) % 360
        self.crab_color = self._hsl_to_hex(hue_shift, 0.8, 0.5)
        
        # Invincibility frames
        self.invincible_until = time.time() + 2.0
        
        # Escalating response
        laugh = random.choice(RESPAWN_LAUGHTER).replace("{n}", str(self.death_count))
        upgrade = random.choice(UPGRADE_INSULTS)
        self.current_message = f"{laugh}\n{upgrade}"
        self.message_color = self.crab_color
        self.message_timer = 4.0
    
    def _hsl_to_hex(self, h, s, l):
        """Simple HSL to hex conversion."""
        h = h / 360.0
        c = (1 - abs(2 * l - 1)) * s
        x = c * (1 - abs((h * 6) % 2 - 1))
        m = l - c / 2
        
        if h < 1/6:
            r, g, b = c, x, 0
        elif h < 2/6:
            r, g, b = x, c, 0
        elif h < 3/6:
            r, g, b = 0, c, x
        elif h < 4/6:
            r, g, b = 0, x, c
        elif h < 5/6:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        r = int((r + m) * 255)
        g = int((g + m) * 255)
        b = int((b + m) * 255)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _game_loop(self):
        now = time.time()
        dt = min(now - self.last_time, 0.1)
        self.last_time = now
        
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        if self.alive:
            # ── Physics ──
            dx = self.mouse_x - self.crab_x
            dy = self.mouse_y - self.crab_y
            dist = math.sqrt(dx*dx + dy*dy)
            
            # Proximity threshold
            flee_radius = 120.0 + (self.death_count * 10)  # gets more paranoid
            
            if dist < flee_radius and dist > 0:
                # PANIC — flee
                self.panic_level = min(self.panic_level + 0.15, 2.0)
                
                # Flee vector (away from cursor)
                flee_x = -dx / dist
                flee_y = -dy / dist
                
                # Speed scales with proximity and death count
                speed = (flee_radius - dist) * 3.0 * (1.0 + self.death_count * 0.2)
                
                self.crab_vx += flee_x * speed * dt
                self.crab_vy += flee_y * speed * dt
                
                # Panic insult cooldown
                if self.panic_insult_cooldown <= 0 and random.random() < 0.02:
                    self.current_message = random.choice(PANIC_INSULTS)
                    self.message_color = "#ff8800"
                    self.message_timer = 1.5
                    self.panic_insult_cooldown = 1.0
                
                # Vibration
                self.vibrate_x = random.uniform(-3, 3) * self.panic_level
                self.vibrate_y = random.uniform(-3, 3) * self.panic_level
            else:
                # Calm — idle drift
                self.panic_level = max(self.panic_level - 0.05, 0.0)
                
                # Random drift
                if random.random() < 0.05:
                    self.crab_vx += random.uniform(-0.5, 0.5)
                    self.crab_vy += random.uniform(-0.5, 0.5)
                
                self.vibrate_x = 0
                self.vibrate_y = 0
                
                # Idle insult cooldown
                if self.panic_level < 0.1 and self.idle_insult_cooldown <= 0 and random.random() < 0.005:
                    self.current_message = random.choice(IDLE_INSULTS)
                    self.message_color = "#00ff41"
                    self.message_timer = 2.5
                    self.idle_insult_cooldown = 2.0
            
            # Friction
            self.crab_vx *= 0.92
            self.crab_vy *= 0.92
            
            # Clamp velocity
            max_speed = 8.0 + self.death_count * 0.5
            speed = math.sqrt(self.crab_vx**2 + self.crab_vy**2)
            if speed > max_speed:
                self.crab_vx = (self.crab_vx / speed) * max_speed
                self.crab_vy = (self.crab_vy / speed) * max_speed
            
            # Move
            self.crab_x += self.crab_vx
            self.crab_y += self.crab_vy
            
            # Boundary bounce
            margin = self.crab_size + 20
            if self.crab_x < margin:
                self.crab_x = margin
                self.crab_vx = abs(self.crab_vx) * 0.8
            elif self.crab_x > w - margin:
                self.crab_x = w - margin
                self.crab_vx = -abs(self.crab_vx) * 0.8
            
            if self.crab_y < margin:
                self.crab_y = margin
                self.crab_vy = abs(self.crab_vy) * 0.8
            elif self.crab_y > h - margin:
                self.crab_y = h - margin
                self.crab_vy = -abs(self.crab_vy) * 0.8
            
            # Cooldowns
            self.panic_insult_cooldown = max(0, self.panic_insult_cooldown - dt)
            self.idle_insult_cooldown = max(0, self.idle_insult_cooldown - dt)
        
        # Message timer
        self.message_timer = max(0, self.message_timer - dt)
        
        # ── Render ──
        self.canvas.delete("all")
        
        # Background grid effect
        for i in range(0, w, 40):
            self.canvas.create_line(i, 0, i, h, fill="#111111")
        for i in range(0, h, 40):
            self.canvas.create_line(0, i, w, i, fill="#111111")
        
        if self.alive:
            self._draw_crab()
        else:
            self._draw_death()
        
        self._draw_ui(w, h)
        
        self.root.after(16, self._game_loop)
    
    def _draw_crab(self):
        x = self.crab_x + self.vibrate_x
        y = self.crab_y + self.vibrate_y
        s = self.crab_size
        
        # Invincibility flash
        if time.time() < self.invincible_until:
            if int(time.time() * 10) % 2 == 0:
                return  # flash on/off
        
        # Shadow
        self.canvas.create_oval(
            x - s * 0.8, y + s * 0.3,
            x + s * 0.8, y + s * 0.6,
            fill="#000000", outline=""
        )
        
        # Body
        body_color = self.crab_color
        self.canvas.create_oval(
            x - s, y - s * 0.6,
            x + s, y + s * 0.4,
            fill=body_color, outline="#000000", width=2
        )
        
        # Shell pattern
        self.canvas.create_oval(
            x - s * 0.6, y - s * 0.3,
            x + s * 0.6, y + s * 0.2,
            outline="#000000", width=1, fill=""
        )
        
        # Eyes
        eye_y = y - s * 0.2
        eye_offset = s * 0.35
        eye_size = s * 0.2
        
        # Panic eyes are wider
        if self.panic_level > 0.5:
            eye_size = s * 0.3
        
        self.canvas.create_oval(
            x - eye_offset - eye_size, eye_y - eye_size,
            x - eye_offset + eye_size, eye_y + eye_size,
            fill=self.eye_color, outline="#000000", width=1
        )
        self.canvas.create_oval(
            x + eye_offset - eye_size, eye_y - eye_size,
            x + eye_offset + eye_size, eye_y + eye_size,
            fill=self.eye_color, outline="#000000", width=1
        )
        
        # Pupils (look toward mouse)
        dx = self.mouse_x - x
        dy = self.mouse_y - y
        dist = max(math.sqrt(dx*dx + dy*dy), 1)
        pupil_offset = eye_size * 0.4
        px = (dx / dist) * pupil_offset
        py = (dy / dist) * pupil_offset
        
        pupil_size = eye_size * 0.5
        self.canvas.create_oval(
            x - eye_offset + px - pupil_size, eye_y + py - pupil_size,
            x - eye_offset + px + pupil_size, eye_y + py + pupil_size,
            fill="#000000", outline=""
        )
        self.canvas.create_oval(
            x + eye_offset + px - pupil_size, eye_y + py - pupil_size,
            x + eye_offset + px + pupil_size, eye_y + py + pupil_size,
            fill="#000000", outline=""
        )
        
        # Claws
        claw_y = y + s * 0.1
        claw_extend = s * 0.9
        
        # Panic claws are raised
        if self.panic_level > 0.5:
            claw_y -= s * 0.3
            claw_extend *= 1.2
        
        # Left claw
        self._draw_claw(x - claw_extend, claw_y, s * 0.4, "left")
        # Right claw
        self._draw_claw(x + claw_extend, claw_y, s * 0.4, "right")
        
        # Legs (3 each side)
        for i in range(3):
            leg_y = y + s * (0.1 + i * 0.12)
            leg_len = s * 0.7
            wobble = math.sin(time.time() * 8 + i) * 5 if self.panic_level > 0.5 else 0
            
            # Left legs
            self.canvas.create_line(
                x - s * 0.7, leg_y,
                x - s * 0.7 - leg_len + wobble, leg_y + s * 0.3,
                fill=body_color, width=2
            )
            # Right legs
            self.canvas.create_line(
                x + s * 0.7, leg_y,
                x + s * 0.7 + leg_len - wobble, leg_y + s * 0.3,
                fill=body_color, width=2
            )
        
        # Panic sweat drops
        if self.panic_level > 1.0:
            for _ in range(3):
                sx = x + random.uniform(-s, s)
                sy = y - s * 0.8 + random.uniform(-s * 0.3, s * 0.3)
                self.canvas.create_text(
                    sx, sy, text="💧", font=("Arial", 8)
                )
    
    def _draw_claw(self, x, y, size, side):
        """Draw a pincer claw."""
        direction = -1 if side == "left" else 1
        
        # Arm
        arm_x = x + direction * size * 0.3
        self.canvas.create_line(
            x, y, arm_x, y - size * 0.3,
            fill=self.crab_color, width=3
        )
        
        # Pincer top
        self.canvas.create_line(
            arm_x, y - size * 0.3,
            arm_x + direction * size * 0.4, y - size * 0.5,
            fill=self.crab_color, width=3
        )
        # Pincer bottom
        self.canvas.create_line(
            arm_x, y - size * 0.3,
            arm_x + direction * size * 0.4, y - size * 0.1,
            fill=self.crab_color, width=3
        )
    
    def _draw_death(self):
        """Draw death animation."""
        x = self.crab_x
        y = self.crab_y
        s = self.crab_size
        
        # Explosion particles
        for i in range(12):
            angle = (i / 12) * math.pi * 2 + self.death_frame * 0.1
            dist = self.death_frame * 15
            px = x + math.cos(angle) * dist
            py = y + math.sin(angle) * dist
            size = max(2, 8 - self.death_frame)
            
            colors = ["#ff0000", "#ff4400", "#ff8800", "#ffcc00", "#ffffff"]
            color = random.choice(colors)
            
            self.canvas.create_oval(
                px - size, py - size, px + size, py + size,
                fill=color, outline=""
            )
        
        # X eyes
        eye_y = y - s * 0.2
        eye_offset = s * 0.35
        for offset in [-eye_offset, eye_offset]:
            self.canvas.create_line(
                x + offset - 5, eye_y - 5, x + offset + 5, eye_y + 5,
                fill="#ff0000", width=2
            )
            self.canvas.create_line(
                x + offset + 5, eye_y - 5, x + offset - 5, eye_y + 5,
                fill="#ff0000", width=2
            )
        
        # Dead body (upside down)
        self.canvas.create_oval(
            x - s, y - s * 0.3,
            x + s, y + s * 0.7,
            fill="#880000", outline="#000000", width=2
        )
        
        # Legs in air
        for i in range(3):
            leg_y = y - s * (0.1 + i * 0.1)
            self.canvas.create_line(
                x - s * 0.7, leg_y,
                x - s * 0.7 - s * 0.5, leg_y - s * 0.3,
                fill="#880000", width=2
            )
            self.canvas.create_line(
                x + s * 0.7, leg_y,
                x + s * 0.7 + s * 0.5, leg_y - s * 0.3,
                fill="#880000", width=2
            )
        
        self.death_frame += 1
    
    def _draw_ui(self, w, h):
        """Draw the HUD."""
        # Title
        self.canvas.create_text(
            w // 2, 20,
            text="CRAB_GOD",
            fill="#ff4444", font=("Courier", 24, "bold"),
            anchor="center"
        )
        
        # Death counter
        self.canvas.create_text(
            20, 20,
            text=f"DEATHS: {self.death_count}",
            fill="#ff0000", font=("Courier", 12),
            anchor="nw"
        )
        
        # Size
        self.canvas.create_text(
            20, 40,
            text=f"SIZE: {self.crab_size:.0f}",
            fill="#ff8800", font=("Courier", 10),
            anchor="nw"
        )
        
        # Status
        status = "PANIC" if self.panic_level > 0.5 else "NOMINAL"
        status_color = "#ff0000" if self.panic_level > 0.5 else "#00ff41"
        self.canvas.create_text(
            w - 20, 20,
            text=f"STATUS: {status}",
            fill=status_color, font=("Courier", 12),
            anchor="ne"
        )
        
        # Current message
        if self.message_timer > 0:
            msg = self.current_message
            # Word wrap long messages
            max_chars = 60
            if len(msg) > max_chars:
                words = msg.split()
                lines = []
                current = ""
                for word in words:
                    if len(current) + len(word) + 1 <= max_chars:
                        current += (" " if current else "") + word
                    else:
                        lines.append(current)
                        current = word
                if current:
                    lines.append(current)
                msg = "\n".join(lines)
            
            msg_y = h - 60
            # Background box
            bbox = self.canvas.bbox(
                self.canvas.create_text(
                    w // 2, msg_y, text=msg,
                    font=("Courier", 11), anchor="center"
                )
            )
            if bbox:
                self.canvas.create_rectangle(
                    bbox[0] - 10, bbox[1] - 5,
                    bbox[2] + 10, bbox[3] + 5,
                    fill="#0a0a0a", outline="#333333"
                )
            self.canvas.create_text(
                w // 2, msg_y,
                text=msg,
                fill=self.message_color,
                font=("Courier", 11),
                anchor="center"
            )
        
        # Instructions
        self.canvas.create_text(
            w // 2, h - 15,
            text="click the crab to kill it. it will judge you.",
            fill="#444444", font=("Courier", 9),
            anchor="center"
        )


if __name__ == "__main__":
    print("[CRAB_GOD] Initializing sovereign insult crab...")
    print("[CRAB_GOD] Click the crab to kill it.")
    print("[CRAB_GOD] It will remember.")
    CrabGod()
