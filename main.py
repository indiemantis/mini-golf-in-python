import pygame
import sys
import math
import random

pygame.init()

WIDTH,HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Golf")


win=pygame.mixer.Sound("/win.mp3")
conq=pygame.mixer.Sound("/conq.wav")
hit=pygame.mixer.Sound("/hit.mp3")
shot=pygame.mixer.Sound("/shot.wav")

WHITE = (255,255,255)
LIGHT_GREEN = (0,0,0)
DARK_GREEN = (0,0,0)
BLACK = (0,0,0)
PARTY_COLORS = [(0,0,0)]

ball_pos = [100, 300]
ball_radius = 15
hole_radius = 20
checker_size = 100
power = 0
max_power = 20
is_dragging = False
start_drag_pos = None
ball_velocity = [0, 0]
friction = 0.98
max_trail_length = 20
trail = []
score = 0
level="EASY  +3"
hlevel=0
particles = []

font = pygame.font.SysFont(None, 36)
score_font = pygame.font.SysFont(None, 48)

def place_hole():
    return [
        random.randint(100,WIDTH - 100),
        random.randint(100,HEIGHT - 100)
    ]

hole_pos = place_hole()

def create_particles(position):
    for _ in range(50):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 6)
        size = random.randint(3, 8)
        lifetime = random.randint(30, 60)
        color = random.choice(PARTY_COLORS)
        particles.append({
            'x': position[0],
            'y': position[1],
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed,
            'size': size,
            'lifetime': lifetime,
            'color': color
        })

def update_particles():
    for particle in particles[:]:
        particle['x'] += particle['vx']
        particle['y'] += particle['vy']
        particle['vy'] += 0.1  # Gravity
        particle['lifetime'] -= 1
        if particle['lifetime'] <= 0:
            particles.remove(particle)

def draw_particles():
    for particle in particles:
        alpha = min(255, particle['lifetime'] * 5)
        color = (*particle['color'], alpha)
        particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, color, (particle['size'], particle['size']), particle['size'])
        screen.blit(particle_surface, (particle['x'] - particle['size'], particle['y'] - particle['size']))


def draw_checkerboard():
    for y in range(0,HEIGHT,checker_size):
        for x in range(0,WIDTH,checker_size):
            if (x//checker_size + y//checker_size) % 2 == 0:
                color = LIGHT_GREEN
            else:
                color = DARK_GREEN
            pygame.draw.rect(screen, color, (x, y, checker_size, checker_size))

def reset_ball():
    global ball_pos, ball_velocity
    ball_pos = [100,300]
    ball_velocity = [0, 0]
    trial=[]


def draw_power_line(start, end):
    pygame.draw.line(screen, BLACK, start, end, 6)
    
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    arrow_length = 15
    arrow_angle1 = angle + math.pi * 0.8
    arrow_angle2 = angle - math.pi * 0.8
    
    point1 = (
        end[0] + arrow_length * math.cos(arrow_angle1),
        end[1] + arrow_length * math.sin(arrow_angle1)
    )
    point2 = (
        end[0] + arrow_length * math.cos(arrow_angle2),
        end[1] + arrow_length * math.sin(arrow_angle2)
    )
    
    pygame.draw.line(screen, BLACK, end, point1, 6)
    pygame.draw.line(screen, BLACK, end, point2, 6)

def draw_trail():
    if len(trail) > 1:
        for i in range(len(trail) - 1):
            alpha = int(255 * (i / len(trail)))
            trail_color = (255, 255, 255, alpha)
            trail_surface = pygame.Surface((ball_radius * 2, ball_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, trail_color, (ball_radius, ball_radius), ball_radius * (i / len(trail)))
            screen.blit(trail_surface, (trail[i][0] - ball_radius, trail[i][1] - ball_radius))

def check_win():
    distance = math.sqrt((ball_pos[0] - hole_pos[0])**2 + (ball_pos[1] - hole_pos[1])**2) 
    return distance < (hole_radius + 10) - ball_radius 

def draw_window_border():
    pygame.draw.rect(screen ,BLACK, (0,0,WIDTH,HEIGHT),5)

def draw_score():
    score_text = score_font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (20, 20))
    score_text = score_font.render(f"{level}", True, BLACK)
    screen.blit(score_text, (20, 60))

def main():
    global ball_pos, is_dragging, start_drag_pos, ball_velocity, hole_pos, power, trail, score,particles,LIGHT_GREEN,DARK_GREEN,level,hlevel
    clock=pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if math.sqrt((event.pos[0] - ball_pos[0])**2 + (event.pos[1] - ball_pos[1])**2) < ball_radius * 2:
                    is_dragging = True
                    start_drag_pos = event.pos
                    
            if event.type == pygame.MOUSEBUTTONUP and is_dragging:
                is_dragging = False
                end_drag_pos = event.pos
                
                dx = start_drag_pos[0] - end_drag_pos[0]
                dy = start_drag_pos[1] - end_drag_pos[1]
                distance = math.sqrt(dx*dx + dy*dy)
                power = min(distance / 10, max_power)
                
                if distance > 5:
                    ball_velocity[0]=dx*0.1
                    ball_velocity[1]=dy*0.1
                    if score<50:
                        score-=1
                        hit.play()

            
            if event.type == pygame.KEYDOWN and event.K_r:
                reset_ball()
                hole_pos= place_hole()
                particles = []
                score = 0

        ball_pos[0]+=ball_velocity[0]
        ball_pos[1]+=ball_velocity[1]
        
        if any(ball_velocity):
            trail.append((ball_pos[0], ball_pos[1]))
            if len(trail) > max_trail_length:
                trail.pop(0)
        
        ball_velocity[0]*=friction
        ball_velocity[1]*=friction
        if abs(ball_velocity[0]) < 0.1 and abs(ball_velocity[1]) < 0.1:
            ball_velocity = [0, 0]
            trail = []

        if ball_pos[0]<ball_radius:
            ball_pos[0]= ball_radius
            ball_velocity[0]*=-0.5
            hit.play()
        if ball_pos[0]>WIDTH-ball_radius:
            ball_pos[0]=WIDTH-ball_radius
            ball_velocity[0]*=-0.5
            hit.play()
        if ball_pos[1]<ball_radius:
            ball_pos[1]= ball_radius
            ball_velocity[1]*=-0.5
            hit.play()
        if ball_pos[1]>HEIGHT-ball_radius:
            ball_pos[1]=HEIGHT-ball_radius
            ball_velocity[1]*=-0.5
            hit.play()
        
        if check_win():
            win.play()
            create_particles(hole_pos)
            if score<20:
                score += 4
            elif score<30:
                score += 3
            elif score<40:
                score += 2
                hlevel=0
            else:
                score += 1
                hlevel+=1
            reset_ball()
            hole_pos = place_hole()
        
        update_particles()
        if score<20:
                DARK_GREEN = (0, 100, 0)
                LIGHT_GREEN = (30, 250, 10)
                level="EASY  +3"
        elif score<30:
                DARK_GREEN = (161, 134, 0)
                LIGHT_GREEN = (255, 238, 0)
                level="NORMAL  +2"
        elif score<40:
                DARK_GREEN = (158, 69, 0)
                LIGHT_GREEN = (255, 111, 0)
                level="HARD  +1"
        elif score<50:
                DARK_GREEN = (102, 10, 0)
                LIGHT_GREEN = (214, 21, 0)
                level=f"SURVIVE  {hlevel}/10"
                if hlevel == 10:
                    level="CONQUERER"
                    score=10000
                    conq.play()
                    hlevel=0
        
        draw_checkerboard()
        pygame.draw.circle(screen, BLACK, hole_pos, hole_radius)
        draw_trail()
        if is_dragging and start_drag_pos:
            mouse_pos = pygame.mouse.get_pos()
            arrow_start = (ball_pos[0], ball_pos[1])
            arrow_end = (2*ball_pos[0] - mouse_pos[0], 2*ball_pos[1] - mouse_pos[1])
            draw_power_line(arrow_start, arrow_end)
        pygame.draw.circle(screen, WHITE, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)
        draw_particles()
        draw_score()
        draw_window_border()
        pygame.display.flip()
        clock.tick(60)



if __name__ == "__main__":
    main()
