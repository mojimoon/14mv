const clueTypes = {
    "V": (i, j, m=mines) => {
      let neighbors = 0;
      for (let ni = i-1; ni <= i+1; ni++) {
        for (let nj = j-1; nj <= j+1; nj++) {
          if (ni >= 0 && ni < cols && nj >= 0 && nj < rows && m[ni][nj]) {
            neighbors++;
          }
        }
      }
      return neighbors;
    },
    "M": (i, j, m=mines) => {
      let neighbors = 0;
      for (let ni = i-1; ni <= i+1; ni++) {
        for (let nj = j-1; nj <= j+1; nj++) {
          if (ni >= 0 && ni < cols && nj >= 0 && nj < rows && m[ni][nj]) {
            neighbors += (ni+nj) % 2 !== 0 ? 2 : 1;
          }
        }
      }
      return neighbors;
    },
    "L": (i, j, m=mines) => {
      let neighbors = 0;
      for (let ni = i-1; ni <= i+1; ni++) {
        for (let nj = j-1; nj <= j+1; nj++) {
          if (ni >= 0 && ni < cols && nj >= 0 && nj < rows && m[ni][nj]) {
            neighbors++;
          }
        }
      }
      return neighbors + (lie[i][j] ? 1 : -1);
    },
    "W": (i, j, m=mines) => {
      const offs = [[-1, -1], [-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1], [0, -1]];
      let neighbors = [];
      let lastNeighborWasMine = false;
      let neighbor1WasMine = false;
      let neighbor8WasMine = false;
      for (const [ioff, joff] of offs) {
        const ni = i-ioff;
        const nj = j-joff;
        if (ni >= 0 && ni < cols && nj >= 0 && nj < rows && m[ni][nj]) {
          if (!lastNeighborWasMine) {
            neighbors.push(0);
          }
          neighbors[neighbors.length-1]++;
          lastNeighborWasMine = true;
          if (ioff === -1 && joff === -1) {
            neighbor1WasMine = true;
          } else if (ioff === 0 && joff === -1) {
            neighbor8WasMine = true;
          }
        } else {
          lastNeighborWasMine = false;
        }
      }
      if (neighbor1WasMine && neighbor8WasMine) {
        neighbors[0] += neighbors.pop();
      }
      if (neighbors.length === 0) {
        neighbors.push(0);
      }
      neighbors.sort((a, b) => a - b);
      return neighbors.join(" ");
    },
    "N": (i, j, m=mines) => {
      let neighbors = 0;
      for (let ni = i-1; ni <= i+1; ni++) {
        for (let nj = j-1; nj <= j+1; nj++) {
          if (ni >= 0 && ni < cols && nj >= 0 && nj < rows && m[ni][nj]) {
            neighbors += (ni+nj) % 2 !== 0 ? -1 : 1;
          }
        }
      }
      return abs(neighbors);
    },
    "X": (i, j, m=mines) => {
      let neighbors = 0;
      if (j-1 >= 0)   neighbors += m[i][j-1];
      if (j-2 >= 0)   neighbors += m[i][j-2];
      if (i+1 < cols) neighbors += m[i+1][j];
      if (i+2 < cols) neighbors += m[i+2][j];
      if (j+1 < rows) neighbors += m[i][j+1];
      if (j+2 < rows) neighbors += m[i][j+2];
      if (i-1 >= 0)   neighbors += m[i-1][j];
      if (i-2 >= 0)   neighbors += m[i-2][j];
      return neighbors;
    },
    "P": (i, j, m=mines) => {
      const offs = [[-1, -1], [-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1], [0, -1]];
      let neighbors = [];
      let lastNeighborWasMine = false;
      let neighbor1WasMine = false;
      let neighbor8WasMine = false;
      for (const [ioff, joff] of offs) {
        const ni = i-ioff;
        const nj = j-joff;
        if (ni >= 0 && ni < cols && nj >= 0 && nj < rows && m[ni][nj]) {
          if (!lastNeighborWasMine) {
            neighbors.push(0);
          }
          neighbors[neighbors.length-1]++;
          lastNeighborWasMine = true;
          if (ioff === -1 && joff === -1) {
            neighbor1WasMine = true;
          } else if (ioff === 0 && joff === -1) {
            neighbor8WasMine = true;
          }
        } else {
          lastNeighborWasMine = false;
        }
      }
      if (neighbor1WasMine && neighbor8WasMine) {
        neighbors[0] += neighbors.pop();
      }
      return neighbors.length;
    },
    "E": (i, j, m=mines) => {
      let posI = i;
      let posJ = j;
      let total = 0;
      while (posJ >= 0 && !m[posI][posJ]) {
        posJ--;
        total++;
      }
      posJ = j;
      while (posI < cols && !m[posI][posJ]) {
        posI++;
        total++;
      }
      posI = i;
      while (posJ < rows && !m[posI][posJ]) {
        posJ++;
        total++;
      }
      posJ = j;
      while (posI >= 0 && !m[posI][posJ]) {
        posI--;
        total++;
      }
      return total - 3; // Subtract 3 because this code would count the clue cell itself 4 times;
    },
    "MN": (i, j, m=mines) => {
      let neighbors = 0;
      for (let ni = i-1; ni <= i+1; ni++) {
        for (let nj = j-1; nj <= j+1; nj++) {
          if (ni >= 0 && ni < cols && nj >= 0 && nj < rows && m[ni][nj]) {
            neighbors += (ni+nj) % 2 !== 0 ? 2 : -1;
          }
        }
      }
      return abs(neighbors);
    },
    "MX": (i, j, m=mines) => {
      let neighbors = 0;
      if (j-1 >= 0)   neighbors += m[i][j-1] * ((i + j - 1) % 2 !== 0 ? 2 : 1);
      if (j-2 >= 0)   neighbors += m[i][j-2] * ((i + j - 2) % 2 !== 0 ? 2 : 1);
      if (i+1 < cols) neighbors += m[i+1][j] * ((i + j + 1) % 2 !== 0 ? 2 : 1);
      if (i+2 < cols) neighbors += m[i+2][j] * ((i + j + 2) % 2 !== 0 ? 2 : 1);
      if (j+1 < rows) neighbors += m[i][j+1] * ((i + j + 1) % 2 !== 0 ? 2 : 1);
      if (j+2 < rows) neighbors += m[i][j+2] * ((i + j + 2) % 2 !== 0 ? 2 : 1);
      if (i-1 >= 0)   neighbors += m[i-1][j] * ((i + j - 1) % 2 !== 0 ? 2 : 1);
      if (i-2 >= 0)   neighbors += m[i-2][j] * ((i + j - 2) % 2 !== 0 ? 2 : 1);
      return neighbors;
    },
    "NX": (i, j, m=mines) => {
      let neighbors = 0;
      if (j-1 >= 0)   neighbors += m[i][j-1] * ((i + j - 1) % 2 !== 0 ? -1 : 1);
      if (j-2 >= 0)   neighbors += m[i][j-2] * ((i + j - 2) % 2 !== 0 ? -1 : 1);
      if (i+1 < cols) neighbors += m[i+1][j] * ((i + j + 1) % 2 !== 0 ? -1 : 1);
      if (i+2 < cols) neighbors += m[i+2][j] * ((i + j + 2) % 2 !== 0 ? -1 : 1);
      if (j+1 < rows) neighbors += m[i][j+1] * ((i + j + 1) % 2 !== 0 ? -1 : 1);
      if (j+2 < rows) neighbors += m[i][j+2] * ((i + j + 2) % 2 !== 0 ? -1 : 1);
      if (i-1 >= 0)   neighbors += m[i-1][j] * ((i + j - 1) % 2 !== 0 ? -1 : 1);
      if (i-2 >= 0)   neighbors += m[i-2][j] * ((i + j - 2) % 2 !== 0 ? -1 : 1);
      return abs(neighbors);
    },
    "MNX": (i, j, m=mines) => {
      let neighbors = 0;
      if (j-1 >= 0)   neighbors += m[i][j-1] * ((i + j - 1) % 2 !== 0 ? -1 : 2);
      if (j-2 >= 0)   neighbors += m[i][j-2] * ((i + j - 2) % 2 !== 0 ? -1 : 2);
      if (i+1 < cols) neighbors += m[i+1][j] * ((i + j + 1) % 2 !== 0 ? -1 : 2);
      if (i+2 < cols) neighbors += m[i+2][j] * ((i + j + 2) % 2 !== 0 ? -1 : 2);
      if (j+1 < rows) neighbors += m[i][j+1] * ((i + j + 1) % 2 !== 0 ? -1 : 2);
      if (j+2 < rows) neighbors += m[i][j+2] * ((i + j + 2) % 2 !== 0 ? -1 : 2);
      if (i-1 >= 0)   neighbors += m[i-1][j] * ((i + j - 1) % 2 !== 0 ? -1 : 2);
      if (i-2 >= 0)   neighbors += m[i-2][j] * ((i + j - 2) % 2 !== 0 ? -1 : 2);
      return abs(neighbors);
    },
    "MNXL": (i, j, m=mines) => {
      let neighbors = 0;
      if (j-1 >= 0)   neighbors += m[i][j-1] * ((i + j - 1) % 2 !== 0 ? -1 : 2);
      if (j-2 >= 0)   neighbors += m[i][j-2] * ((i + j - 2) % 2 !== 0 ? -1 : 2);
      if (i+1 < cols) neighbors += m[i+1][j] * ((i + j + 1) % 2 !== 0 ? -1 : 2);
      if (i+2 < cols) neighbors += m[i+2][j] * ((i + j + 2) % 2 !== 0 ? -1 : 2);
      if (j+1 < rows) neighbors += m[i][j+1] * ((i + j + 1) % 2 !== 0 ? -1 : 2);
      if (j+2 < rows) neighbors += m[i][j+2] * ((i + j + 2) % 2 !== 0 ? -1 : 2);
      if (i-1 >= 0)   neighbors += m[i-1][j] * ((i + j - 1) % 2 !== 0 ? -1 : 2);
      if (i-2 >= 0)   neighbors += m[i-2][j] * ((i + j - 2) % 2 !== 0 ? -1 : 2);
      return abs(neighbors + (lie[i][j] ? 1 : -1));
    },
    "XW": (i, j, m=mines) => {
      let neighbors = [];
      if (j-1 >= 0) {
        if (j-2 >= 0) neighbors.push(m[i][j-2] + m[i][j-1]);
        else neighbors.push(m[i][j-1]);
      }
      if (i+1 < cols) {
        if (i+2 < cols) neighbors.push(m[i+1][j] + m[i+2][j]);
        else neighbors.push(m[i+1][j]);
      }
      if (j+1 < rows) {
        if (j+2 < rows) neighbors.push(m[i][j+1] + m[i][j+2]);
        else neighbors.push(m[i][j+1]);
      }
      if (i-1 >= 0) {
        if (i-2 >= 0) neighbors.push(m[i-1][j] + m[i-2][j]);
        else neighbors.push(m[i-1][j]);
      }
      neighbors = neighbors.filter(n => n !== 0);
      if (neighbors.length === 0) {
        neighbors.push(0);
      }
      neighbors.sort((a, b) => a - b);
      return neighbors.join(" ");
    },
    "XP": (i, j, m=mines) => {
      let neighbors = 0;
      if (j-1 >= 0 && (m[i][j-1] || (j-2 >= 0 && m[i][j-2]))) neighbors++;
      if (i+1 < cols && (m[i+1][j] || (i+2 < cols && m[i+2][j]))) neighbors++;
      if (j+1 < rows && (m[i][j+1] || (j+2 < rows && m[i][j+2]))) neighbors++;
      if (i-1 >= 0 && (m[i-1][j] || (i-2 >= 0 && m[i-2][j]))) neighbors++;
      return neighbors;
    },
    "WE": (i, j, m=mines) => {
      let neighbors = [];
      let posI = i;
      let posJ = j;
      let cur = 0;
      for (cur = 0, posJ = j-1; posJ >= 0 && !m[i][posJ]; posJ--) { cur++; }
      if (cur > 0) { neighbors.push(cur); }
      for (cur = 0, posI = i+1; posI < cols && !m[posI][j]; posI++) { cur++; }
      if (cur > 0) { neighbors.push(cur); }
      for (cur = 0, posJ = j+1; posJ < rows && !m[i][posJ]; posJ++) { cur++; }
      if (cur > 0) { neighbors.push(cur); }
      for (cur = 0, posI = i-1; posI >= 0 && !m[posI][j]; posI--) { cur++; }
      if (cur > 0) { neighbors.push(cur); }
      // neighbors = neighbors.filter(n => n !== 0);
      if (neighbors.length === 0) {
        neighbors.push(0);
      }
      neighbors.sort((a, b) => a - b);
      return neighbors.join(" ");
    },
    "B3": (i, j, m=mines) => {
      return base3DigitSum(clueTypes.V(i, j, m));
    },
    "MB3": (i, j, m=mines) => {
      return base3DigitSum(clueTypes.M(i, j, m));
    },
    "#": (i, j, m=mines) => {
      const ct = clueType[i][j];
      return clueTypes[ct](i, j, m);
    },
    "MM": (i, j, m=mines) => {
      return clueTypes.M(i, j, m) % 3;
    },
    "EV": (i, j, m=mines) => {
      let neighbors = 0;
      for (let ni = i-1; ni <= i+1; ni++) {
        for (let nj = j-1; nj <= j+1; nj++) {
          if (ni >= 0 && ni < cols && nj >= 0 && nj < rows) {
            neighbors += clueTypes.V(ni, nj, m);
          }
        }
      }
      return neighbors;
    },
    // "EE": (i, j, m=mines) => {
    //   let posI = i;
    //   let posJ = j;
    //   let base = clueTypes.E(i, j, m);
    //   let total = 0;
    //   while (posJ >= 0 && !m[posI][posJ]) {
    //     posJ--;
    //     total += clueTypes.E(i, posJ, m);
    //   }
    //   posJ = j;
    //   while (posI < cols -1 && !m[posI][posJ]) {
    //     posI++;
    //     total += clueTypes.E(posI, j, m);
    //   }
    //   posI = i;
    //   while (posJ < rows && !m[posI][posJ]) {
    //     posJ++;
    //     total += clueTypes.E(i, posJ, m);
    //   }
    //   posJ = j;
    //   while (posI > 0 && !m[posI][posJ]) {
    //     posI--;
    //     total += clueTypes.E(posI, j, m);
    //   }
    //   return total - 3 * base;
    // }
  }
  
  const getNeighbors = clueTypes.WE;
  
  // Normal minesweeper clues
  
  // Mines in shaded cells count as two
  
  // Each clue is either one more or one less than it should be
  
  // Tapa clues
  
  // Clues indicate the difference between mines on shaded cells and mines on unshaded cells
  
  // Clues focus on the 5x5 "plus shape" around them rather than the 3x3 box
  
  // Like Tapa clues, but the clues only show the number of groups rather than the groups themselves
  
  // Number of non-mine squares visible from the clue square (including the clue square itself)

  function base3DigitSum(n) {
    return n.toString(3).split("").reduce((a, b) => a + parseInt(b), 0);
  }