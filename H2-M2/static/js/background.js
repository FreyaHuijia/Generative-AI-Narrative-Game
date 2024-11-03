let particles = [];

function setup() {
    const canvas = createCanvas(windowWidth, windowHeight);
    canvas.position(0, 0);
    canvas.style('z-index', '-1');
    
    // 根据不同场景初始化不同的粒子效果
    for (let i = 0; i < 100; i++) {
        particles.push({
            x: random(width),
            y: random(height),
            size: random(2, 5),
            speedX: random(-1, 1),
            speedY: random(-1, 1)
        });
    }
}

function draw() {
    clear();
    
    // 获取当前选中的场景
    const selectedScenario = document.querySelector('input[type="radio"]:checked');
    
    if (selectedScenario) {
        switch(selectedScenario.value) {
            case 'forest':
                drawForestParticles();
                break;
            case 'canyon':
                drawCanyonParticles();
                break;
            case 'snow':
                drawSnowParticles();
                break;
        }
    }
}

function drawForestParticles() {
    // 绘制萤火虫效果
    particles.forEach(p => {
        fill(255, 255, 150, 150);
        noStroke();
        circle(p.x, p.y, p.size);
        
        p.x += p.speedX;
        p.y += p.speedY;
        
        if (p.x < 0 || p.x > width) p.speedX *= -1;
        if (p.y < 0 || p.y > height) p.speedY *= -1;
    });
}

function drawCanyonParticles() {
    // 绘制沙粒效果
    particles.forEach(p => {
        fill(255, 200, 150, 100);
        noStroke();
        circle(p.x, p.y, p.size);
        
        p.x += p.speedX;
        p.y += p.speedY * 0.5;
        
        if (p.y > height) {
            p.y = 0;
            p.x = random(width);
        }
    });
}

function drawSnowParticles() {
    // 绘制雪花效果
    particles.forEach(p => {
        fill(255, 255, 255, 200);
        noStroke();
        circle(p.x, p.y, p.size);
        
        p.x += sin(frameCount * 0.01) * 0.5;
        p.y += p.speedY;
        
        if (p.y > height) {
            p.y = 0;
            p.x = random(width);
        }
    });
}

function windowResized() {
    resizeCanvas(windowWidth, windowHeight);
}
