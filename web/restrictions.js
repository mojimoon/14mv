const restrictions = {
    "V": (m=mines) => true,
    "Q": (m=mines) => {
      for (let i = 0; i < cols-1; i++) {
        for (let j = 0; j < rows-1; j++) {
          if (!m[i][j] && !m[i+1][j] && !m[i][j+1] && !m[i+1][j+1]) {
            return false;
          }
        }
      }
      return true;
    },
    "C": (m=mines) => {
      // Algorithm:
      // - Locate a mine (doesn't matter which one)
      // - Do a BFS from there
      // - If that hits every mine, return true. Otherwise, return false
      let firstMineI = -1, firstMineJ = -1;
      outer: for (let i = 0; i < cols; i++) {
        for (let j = 0; j < rows; j++) {
          if (m[i][j]) {
            firstMineI = i;
            firstMineJ = j;
            break outer;
          }
        }
      }
      let visited = Array(cols).fill().map(_ => Array(rows).fill(0));
      let queue = [[firstMineI, firstMineJ]];
      while (queue.length > 0) {
        const [i, j] = queue.shift();
        visited[i][j] = 1;
        for (let ni = i-1; ni <= i+1; ni++) {
          for (let nj = j-1; nj <= j+1; nj++) {
            if (ni >= 0 && ni < cols && nj >= 0 && nj < rows && !visited[ni][nj] && m[ni][nj]) {
              queue.push([ni, nj]);
            }
          }
        }
      }
      for (let i = 0; i < cols; i++) {
        for (let j = 0; j < rows; j++) {
          if (!visited[i][j] && m[i][j]) {
            return false;
          }
        }
      }
      return true;
    },
    "T": (m=mines) => {
      for (let i = 0; i < cols; i++) {
        for (let j = 0; j < rows; j++) {
          if (i < cols-2 && m[i][j] && m[i+1][j] && m[i+2][j]) {
            return false;
          }
          if (j < rows-2 && m[i][j] && m[i][j+1] && m[i][j+2]) {
            return false;
          }
          if (i < cols-2 && j < rows-2) {
            if (m[i][j] && m[i+1][j+1] && m[i+2][j+2]) {
              return false;
            }
            if (m[i][j+2] && m[i+1][j+1] && m[i+2][j]) {
              return false;
            }
          }
        }
      }
      return true;
    },
    "D": (m=mines) => {
      for (let i = 0; i < cols; i++) {
        for (let j = 0; j < rows; j++) {
          if (m[i][j]) {
            let adjacent = 0;
            if (j-1 >= 0)   adjacent += m[i][j-1];
            if (i+1 < cols) adjacent += m[i+1][j];
            if (j+1 < rows) adjacent += m[i][j+1];
            if (i-1 >= 0)   adjacent += m[i-1][j];
            if (adjacent !== 1) {
              return false;
            }
          }
        }
      }
      return true;
    },
    "S": (m=mines) => {
      let oneCount = 0;
      let twoCount = 0;
      for (let i = 0; i < cols; i++) {
        for (let j = 0; j < rows; j++) {
          if (m[i][j]) {
            let adjacent = 0;
            if (j-1 >= 0)   adjacent += m[i][j-1];
            if (i+1 < cols) adjacent += m[i+1][j];
            if (j+1 < rows) adjacent += m[i][j+1];
            if (i-1 >= 0)   adjacent += m[i-1][j];
            if (adjacent === 1) {
              oneCount++;
            } else if (adjacent === 2) {
              twoCount++;
            }
          }
        }
      }
      return restrictions.C(m) && oneCount === 2 && twoCount === numMines-2;
    },
    "B": (m=mines) => {
      const num = numMines / cols;
      for (let i = 0; i < cols; i++) {
        let count = 0;
        for (let j = 0; j < rows; j++) {
          count += m[i][j];
        }
        if (count !== num) {
          return false;
        }
      }
      for (let j = 0; j < rows; j++) {
        let count = 0;
        for (let i = 0; i < cols; i++) {
          count += m[i][j];
        }
        if (count !== num) {
          return false;
        }
      }
      return true;
    },
    "XB": (m=mines) => {
      // All rows and columns must have different numbers of mines
      let rowCounts = Array(rows).fill(0);
      let colCounts = Array(cols).fill(0);
      for (let i = 0; i < cols; i++) {
        for (let j = 0; j < rows; j++) {
          rowCounts[j] += m[i][j];
          colCounts[i] += m[i][j];
        }
      }
      return new Set(rowCounts).size === rows && new Set(colCounts).size === cols;
    },
    // "XM": (m=mines) => {
    //   const center = Math.floor(cols/2);
    //   for (let i = 0; i < center; i++) {
    //     if (i == cols-1-i) {
    //       continue;
    //     }
    //     for (let j = 0; j < rows; j++) {
    //       if (m[i][j] && m[cols-1-i][j]) {
    //         return false;
    //       }
    //     }
    //   }
    // }
  }
  
  const restriction = restrictions.V;
  
  // No restrictions (normal minesweeper)
  
  // Every 2x2 box must contain at least one mine
  
  // All mines must be orthogonally or diagonally connected
  
  // There may be no set of three mines in a row, orthogonally or diagonally
  
  // All mines must come in dominoes that don't touch each other
  
  // All rows and columns must have the same number of mines
  