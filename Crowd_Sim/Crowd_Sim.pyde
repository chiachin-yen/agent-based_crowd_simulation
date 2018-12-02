field = PVector(100,100,0)
bound_vex = []
poi = []
time_factor = 1

def random_p(list_p):
    p = []
    for pair in list_p:
        for i in range(int(pair[1])):
            p.append(pair[0])
    return p[int(random(len(p)))]

def random_g(mean, s):
    k = randomGaussian()
    if k > 2:
        k = 2
    elif k < -2:
        k = -2
        
    return k*s + mean

def inside_polygon(x, y, points):
    """Check if point x y locate in polygon points"""
    n = len(points)
    inside = False
    p1x, p1y = points[0]
    for i in range(1, n + 1):
        p2x, p2y = points[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

class Boid:
    def __init__(self, pos = PVector(0,0,0), velocity=PVector(0,0,0), acceleration = PVector(0,0,0)):
        self.pos = pos
        self.velocity = velocity
        self.acceleration = acceleration
        self.max_acc = 1
        self.temp_pos = PVector(0, 0, 0)
        self.status = 2
        
        self.target = PVector(0, 0, 0)
        self.in_target_mode = False
        
        self.stay_time = 0
        self.in_stay_mode = False
        
        self.roaming_time = 0
        self.in_roaming_mode = False
        
        self.sep = PVector(0, 0, 0)
        self.ali = PVector(0, 0, 0)
        self.coh = PVector(0, 0, 0)
        
        self.remain_time = random_g(300,100) * time_factor
        self.exiting = False
        self.social_pref = random_g(0.5,0.5)
        
        self.max_vel = random_g(1.8, 0.3)
    
    boid_h = 0.5
    boid_w = 0.6
    
    def draw_boid(self):
        """Draw boid with Processing"""
        
        pushMatrix()
        translate(self.pos.x, self.pos.y)

        stroke(128)
        strokeWeight(0.1)
        noStroke()
        if self.status == 0:
            fill(128,128,28,10)
        elif self.status == 1:
            fill(64,192,128,10)
        elif self.status == 2:
            fill(128,128,128,10)
        else:
            fill(255)
        ellipse(0,0, Boid.boid_h,Boid.boid_h)
        '''
        noStroke()
        fill(0)
        if self.velocity.y < 0 :
            rotate(-atan(self.velocity.x / self.velocity.y))
        elif self.velocity.y != 0 :
            rotate(-atan(self.velocity.x / self.velocity.y) - PI)        
        triangle(0, 0,
                 Boid.boid_w / 2, -Boid.boid_h,
                 - Boid.boid_w / 2, -Boid.boid_h)'''
        
        popMatrix()
        
    
    def move(self, i_flock, graph, i):
        """Move Boid with current velovity"""
        self.seperation(i_flock, graph, i)
        

            
        if self.status == 0:
            self.target_mode()
        elif self.status == 1:
            self.stay_mode()
        elif self.status == 2:
            self.roaming_mode()
        elif self.status == 3:
            i_flock.pop(i)
            return None
        
        self.acceleration.add(self.sep.mult(1))
        self.acceleration.add(self.ali.mult(self.social_pref))
        self.bound()            
        
        if self.acceleration.mag() > self.max_acc :
            self.velocity.setMag(self.max_acc)

        self.velocity.add(self.acceleration)
                
        if self.velocity.mag() > self.max_vel :
            self.velocity.setMag(self.max_vel)
            
        if self.status == 2:
            self.velocity.limit(self.max_vel*0.7)
            
        # print('pos',self.pos.x, self.pos.y)
        # print('v', self.velocity.mag())
        # print('a', self.acceleration.mag())
        # print(self.status)
        
        self.pos.add(self.velocity)
        self.acceleration.mult(0)
        self.coh.setMag(0)
        self.sep.setMag(0)
        self.ali.setMag(0)
        self.wrap()
        
        if not inside_polygon(self.pos.x, self.pos.y, poi):
            self.pos.sub(self.velocity)
        
        self.remain_time -= 1
        if self.remain_time < 100 and self.status != 3:
            self.status = 0
            self.target = random_p([(PVector(22,81),1),(PVector(61,81),1)])
            self.in_target_mode = True
            self.exiting = True
        
        if self.remain_time < 0:
            i_flock.pop(i)
        
    def wrap(self):
        """No boundary"""
        if self.pos.x > field.x + Boid.boid_h:
            self.pos.x -= (self.pos.x // field.x) * field.x
        if self.pos.y > field.y + Boid.boid_h:
            self.pos.y -= (self.pos.y // field.y) * field.y
        if self.pos.x < - Boid.boid_h:
            self.pos.x += (((-self.pos.x) // field.x) + 1) * field.x
        if self.pos.y < - Boid.boid_h:
            self.pos.y += (((-self.pos.y) // field.y) + 1) * field.y
    
    def random_steer(self):
        """Test function"""
        self.acceleration.x = random(-0.3, 0.3)
        self.acceleration.y = random(-0.3, 0.3)
    
    def targeting(self):
        """Move to desire location"""
        self.temp = PVector.sub(self.pos, self.target)
        self.temp.normalize()
        self.acceleration.sub(self.temp.setMag(1))
        
    def target_mode(self):
        """Operate a target moving."""
        if not self.in_target_mode:
            # If not in target mode, choose a target
            while not inside_polygon(self.target.x,self.target.y, poi):
                self.target=PVector(random(-1,1),random(-1,1),0)
                self.target.setMag(random_g(20,3))
                self.target.add(self.pos)
                self.target = random_p([(self.target, 3),(self.coh, 2)])
                if self.target.x > field.x:
                    self.target.x = field.x
                elif self.target.x < 0:
                    self.target.x =0
                if self.target.y > field.y:
                    self.target.y = field.y
                elif self.target.y < 0:
                    self.target.y =0
            # print("new target", self.target.x, self.target.y)
            self.in_target_mode = True
        
        if PVector.dist(self.pos, self.target) < 3:
            self.in_target_mode = False
            if self.exiting:
                self.status = 3
            else:
                self.status = random_p([(0,3),(1,6),(2,5)])
        else:
            self.targeting()
            
    def stay_mode(self):
        if not self.in_stay_mode:
            self.stay_time = random(100)
            self.in_stay_mode = True
            
        self.velocity.setMag(0)
        self.ali.setMag(0)
        self.sep.setMag(0.01)*abs(self.social_pref)
        self.acceleration.x = random_g(0, 0.1)
        self.acceleration.y = random_g(0, 0.1)
        self.stay_time -= 1
        # print("stay for", self.stay_time)
        
        if self.stay_time < 0:
            self.status = random_p([(0,5),(1,1),(2,5)])
            self.in_stay_mode = False
            
    def roaming_mode(self):
        if not self.in_roaming_mode:
            self.roaming_time = random_g(40,15)
            self.in_roaming_mode = True
            
        roaming = PVector(random(-0.2, 0.2),random(-0.2, 0.2))
        
        self.acceleration.add(roaming)
        
        self.roaming_time -= 1
        
        if self.roaming_time < 0:
            self.status = random_p([(0,5),(1,5),(2,1)])
            self.in_roaming_mode = False
            
    def seperation(self, i_flock, graph, i):
        count = 0
        count_coh = 0
        for j in range(len(i_flock)):
            dis = graph[i][j]
            if dis > 0 and dis < 3:
                count += 1
                temp = PVector.sub(self.pos, i_flock[j].pos)
                temp.normalize()
                temp.div(dis)
                self.sep.add(temp)
                self.ali.add(i_flock[j].velocity)
            if dis < 15:
                count_coh += 1
                self.coh += i_flock[j].pos

        if count > 0:
            self.sep.div(count)
            self.ali.div(count)
            self.velocity.mult(1-min(count/20, 0.5))
        
        if count_coh > 0:
            self.coh.div(count_coh)
            
    def bound(self):
        min_d = 10
        vex_i = 0
        for i, v in enumerate(bound_vex):
            d = PVector.dist(self.pos, v)
            if d < min_d:
                min_d = d
                vex_i = i
        if min_d < 4:
            self.velocity.setMag(min_d / 4)
        if min_d < 2:
            rep = PVector.sub(bound_vex[vex_i], self.pos)
            self.velocity.setMag(0)
            self.acceleration = rep.setMag(-2)


class flock:
    def __init__(self):
        self.collection = []
        self.graph = []
        
    def add_boid(self, new_boid):
        """Add a new boid to the flock"""
        self.collection.append(new_boid)
        
    def update(self):
        for i, indi_boid in enumerate(self.collection):
            indi_boid.move(self.collection, self.graph, i)
            
    def render(self):
        for i, indi_boid in enumerate(self.collection):
            indi_boid.draw_boid()
    
    def calc_graph(self):
        self.graph = []
        for i, indi_boid in enumerate(self.collection):
            graph_item = []
            for j, target_boid in enumerate(self.collection):
                graph_item.append(PVector.dist(indi_boid.pos, target_boid.pos))
            self.graph.append(graph_item)
        # print(self.graph)
        

new_flock = flock()

def setup():
    size(1000, 1000)
    background(255)
    sh = loadShape("bound.svg").getChild('circle')
    for i in range(sh.getVertexCount()):
        v = sh.getVertex(i)
        bound_vex.append(v.mult(0.6))
        poi.append((v.x,v.y))
    #frameRate(1)
    

def draw():
    # background(255)
    scale(10,10)
    strokeWeight(0.1)
    
    # print(mouseX, mouseY)
    
    pv = bound_vex[-1]
    stroke(0)
    for i in bound_vex:
        # ellipse(i.x,i.y,0.2,0.2)
        line(i.x,i.y,pv.x,pv.y)
        pv = i
    
    print(frameCount, len(new_flock.collection))
    
    new_flock.calc_graph()
    new_flock.update()
    new_flock.render()
    if frameCount % 50 == 0:
        saveFrame("frame-######.png")
    
    if random_p([(True,3),(False,1)]):
        for i in range(int(random_g(15,1))):
            new_flock.add_boid(Boid(pos = PVector(65,random_g(17,1)), velocity = PVector(-1, 0, 0)))
        

def mouseClicked():
    new_flock.add_boid(Boid(pos = PVector(mouseX*0.1,mouseY*0.1,0), velocity = PVector(1, 1, 0)))
