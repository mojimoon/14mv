document.oncontextmenu = _ => {
    return false;
  }
  
  const sz = 50;
  const cols = 5;
  const rows = 5;
  let mines = Array(cols).fill().map(_ => Array(rows).fill(0));
  let revealed = Array(cols).fill().map(_ => Array(rows).fill(1));
  let lie = Array(cols).fill().map(_ => Array(rows).fill().map(_ => Math.random() < 0.5 ? 0 : 1));
  let list = ["V", "M", "L", "W", "N", "X", "P", "E"];
  let clueType = Array(cols).fill().map(_ => Array(rows).fill().map(_ => list[Math.floor(Math.random() * 8)]));
  let numMines = 10;
  let mistakes = 0;
  let drawingMode = false;
  let drawing;
  let chessboard = true;
  
  function setup() {
    createCanvas(windowWidth, windowHeight);
    generatePuzzle();
    drawing = createGraphics(width, height);
  }
  
  function checkClueType(i, j, ct) {
    return getNeighbors === clueTypes[ct] || getNeighbors === clueTypes["#"] && clueType[i][j] === ct;
  }
  
  function keyPressed() {
    if (key === "d") {
      drawingMode = !drawingMode;
    }
  }
  
  // Puzzle generation algorithm
  // - Put mines in random places & reveal everything that's not mines
  // - Unreveal a random cell
  // - See if the unrevealed cell could've been a mine
  //   - If it could've, rereveal the cell and try a different cell
  //   - Otherwise, leave it unrevealed and repeat
  // - Stop when every cell has been eliminated
  // This ensures that all puzzles can be solved without guessing
  function generatePuzzle() {
    let remaining;
    let mineSpots;
    do {
      remaining = numMines;
      mineSpots = [];
      mines = Array(cols).fill().map(_ => Array(rows).fill(0));
      while (remaining > 0) {
        const i = floor(random(cols));
        const j = floor(random(rows));
        if (!mines[i][j]) {
          mines[i][j] = 1;
          revealed[i][j] = 0;
          mineSpots.push([i, j]);
          remaining--;
        }
      }
    } while (!restriction());
    //remaining = 8;
    let options = [];
    for (let i = 0; i < cols; i++) {
      for (let j = 0; j < rows; j++) {
        if (!mines[i][j]) {
          options.push([i, j]);
        }
      }
    }
    //let failures = 3;
    while (options.length > 0) {
      const [i, j] = random(options);
      revealed[i][j] = 0;
      mineSpots.push([i, j]);
      const choices = choose(numMines, mineSpots);
      let found = false;
      outer: for (const c of choices) {
        const choice = c.map(n => mineSpots[n]);
        let newMines = Array(cols).fill().map(_ => Array(rows).fill(0));
        for (const [newI, newJ] of choice) {
          newMines[newI][newJ] = 1;
        }
        if (!newMines[i][j] || !restriction(newMines)) {
          continue;
        }
        for (let newI = 0; newI < cols; newI++) {
          for (let newJ = 0; newJ < rows; newJ++) {
            if (revealed[newI][newJ] && getNeighbors(newI, newJ) !== getNeighbors(newI, newJ, newMines)) {
              continue outer;
            }
          }
        }
        found = true;
      }
      if (found) {
        revealed[i][j] = 1;
        // Does this have to be in here? Idk
        for (let n = mineSpots.length-1; n >= 0; n--) {
          if (mineSpots[n][0] === i && mineSpots[n][1] === j) {
            mineSpots.splice(n, 1);
          }
        }
        // failures--;
        // if (failures <= 0) {
        //   return;
        // }
      }
      for (let n = options.length-1; n >= 0; n--) {
        if (options[n][0] === i && options[n][1] === j) {
          options.splice(n, 1);
        }
      }
    }
  }
  
  // Algorithm to enumerate all ways to choose num elements from arr
  function choose(num, arr, start=0) {
    if (num === 1) {
      let choices = [];
      for (let i = start; i < arr.length; i++) {
        choices.push(i);
      }
      return choices;
    }
    let choices = [];
    for (let i = start; i <= arr.length-num; i++) {
      let subchoices = choose(num-1, arr, i+1);
      subchoices = subchoices.map(x => [i].concat(x));
      choices = choices.concat(subchoices);
    }
    return choices;
  }
  
  function mousePressed() {
    if (!drawingMode) {
      const mx = mouseX -  width/2 + cols*sz/2;
      const my = mouseY - height/2 + rows*sz/2;
      const i = floor(mx / sz);
      const j = floor(my / sz);
      if (mouseButton === LEFT) {
        if (!revealed[i][j]) {
          reveal(i, j, false);
        } else if (!mines[i][j]) {
          for (let ni = i-1; ni <= i+1; ni++) {
            for (let nj = j-1; nj <= j+1; nj++) {
              reveal(ni, nj, false);
            }
          }
        }
      } else if (mouseButton === RIGHT) {
        if (!revealed[i][j]) {
          reveal(i, j, true);
        } else if (!mines[i][j]) {
          for (let ni = i-1; ni <= i+1; ni++) {
            for (let nj = j-1; nj <= j+1; nj++) {
              reveal(ni, nj, true);
            }
          }
        }
      }
    }
  }
  
  function reveal(i, j, isMine) {
    if (i >= 0 && i < cols && j >= 0 && j < rows) {
      if (!isMine && !revealed[i][j]) {
        if (mines[i][j]) {
          mistakes++;
        } else {
          revealed[i][j] = 1;
        }
      } else if (isMine && !revealed[i][j]) {
        if (!mines[i][j]) {
          mistakes++;
        } else {
          revealed[i][j] = 1;
          numMines--;
        }
      }
    }
  }
  
  function draw() {
    background(204);
    if (drawingMode && mouseIsPressed) {
      if (mouseButton === LEFT) {
        drawing.stroke(0);
        drawing.strokeWeight(8);
        drawing.line(pmouseX, pmouseY, mouseX, mouseY);
      } else if (mouseButton === RIGHT) {
        // // hack to make it erase things
        // drawing.stroke(255);
        // drawing.strokeWeight(8);
        // drawing.line(pmouseX, pmouseY, mouseX, mouseY);
        // drawing.loadPixels();
        // const d = drawing.pixelDensity();
        // const minX = min(pmouseX, mouseX)*d;
        // const maxX = max(pmouseX, mouseX)*d;
        // const minY = min(pmouseY, mouseY)*d;
        // const maxY = max(pmouseY, mouseY)*d;
        // for (let x = minX-24; x <= maxX+24; x++) {
        //   for (let y = minY-24; y <= maxY+24; y++) {
        //     const idx = (x + y * drawing.width * d) * 4;
        //     if (drawing.pixels[idx] > 128) {
        //       drawing.pixels[idx+0] = 0;
        //       drawing.pixels[idx+1] = 0;
        //       drawing.pixels[idx+2] = 0;
        //       drawing.pixels[idx+3] = 0;
        //     }
        //   }
        // }
        // drawing.updatePixels();
        drawing.clear();
      }
    }
    push();
    translate(-cols*sz/2, -rows*sz/2);
    translate(width/2, height/2);
    for (let i = 0; i < cols; i++) {
      for (let j = 0; j < rows; j++) {
        if (revealed[i][j]) {
          noStroke();
          if (mines[i][j]) {
            fill(102, 102, 51);
            square(i*sz + sz*0.25, j*sz + sz*0.25, sz*0.5);
          } else {
            let complete = true;
            for (let ni = i-1; ni <= i+1; ni++) {
              for (let nj = j-1; nj <= j+1; nj++) {
                if (ni >= 0 && ni < cols && nj >= 0 && nj < rows && !revealed[ni][nj]) {
                  complete = false;
                }
              }
            }
            if (complete) {
              fill(102);
            } else {
              fill(51);
            }
            textAlign(CENTER, CENTER);
            textSize(sz*0.7);
            const neighbors = getNeighbors(i, j);
            // Spaghetti code to make Tapa clues work
            if (typeof neighbors === "string") {
              if (neighbors.length === 3) {
                textSize(sz*0.5);
                text(neighbors, i*sz + sz*0.5, j*sz + sz*0.5);
              } else if (neighbors.length === 5) {
                textSize(sz*0.5);
                text(neighbors.slice(0, 3), i*sz + sz*0.5, j*sz + sz*0.3);
                text(neighbors[4], i*sz + sz*0.5, j*sz + sz*0.7);
              } else if (neighbors.length === 7) {
                textSize(sz*0.5);
                text(neighbors.slice(0, 3), i*sz + sz*0.5, j*sz + sz*0.3);
                text(neighbors.slice(4, 7), i*sz + sz*0.5, j*sz + sz*0.7);
              } else {
                text(neighbors, i*sz + sz*0.5, j*sz + sz*0.5);
              }
            } else {
              text(neighbors, i*sz + sz*0.5, j*sz + sz*0.5);
            }
            if (getNeighbors === clueTypes["#"]) {
              textAlign(RIGHT, BOTTOM);
              textSize(sz*0.25);
              text(clueType[i][j], i*sz + sz - 2, j*sz + sz - 2);
            }
          }
        }
        stroke(51);
        strokeWeight(sz*0.05);
        noFill();
        square(i*sz, j*sz, sz);
      }
    }
    if (chessboard) {
      for (let i = 0; i < cols; i++) {
        for (let j = 0; j < rows; j++) {
          if ((i+j) % 2 !== 0) {
            noStroke();
            fill(51, 102);
            square(i*sz, j*sz, sz);
          }
        }
      }
    }
    if (!drawingMode) {
      const mx = mouseX -  width/2 + cols*sz/2;
      const my = mouseY - height/2 + rows*sz/2;
      const i = floor(mx / sz);
      const j = floor(my / sz);
      if (i >= 0 && i < cols && j >= 0 && j < rows) {
        noStroke();
        fill(51, 51);
        if (revealed[i][j] && !mines[i][j]) {
          if (checkClueType(i, j, "X")) {
            square(i*sz, j*sz, sz);
            if (j-1 >= 0) square(i*sz, (j-1)*sz, sz);
            if (j-2 >= 0) square(i*sz, (j-2)*sz, sz);
            if (i+1 < cols) square((i+1)*sz, j*sz, sz);
            if (i+2 < cols) square((i+2)*sz, j*sz, sz);
            if (j+1 < rows) square(i*sz, (j+1)*sz, sz);
            if (j+2 < rows) square(i*sz, (j+2)*sz, sz);
            if (i-1 >= 0) square((i-1)*sz, j*sz, sz);
            if (i-2 >= 0) square((i-2)*sz, j*sz, sz);
          } else {
            for (let ni = i-1; ni <= i+1; ni++) {
              for (let nj = j-1; nj <= j+1; nj++) {
                if (ni >= 0 && ni < cols && nj >= 0 && nj < rows) {
                  square(ni*sz, nj*sz, sz);
                }
              }
            }
          }
        } else {
          square(i*sz, j*sz, sz);
        }
      }
    }
    textAlign(LEFT, BOTTOM);
    textSize(20);
    noStroke();
    fill(51);
    text(`Mines remaining: ${numMines}`, 0, -25);
    // text(`Mistakes: ${mistakes}`, 0, -5);
    pop();
    image(drawing, 0, 0);
  }