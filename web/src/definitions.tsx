export enum ClueType {
    V, // [V] Vanilla
    M1, // [1M] Multiple
    L1, // [1L] Liar
    W1, // [1W] Wall
    N1, // [1N] Negative
    X1, // [1X] Cross
    P1, // [1P] Partition
    E1, // [1E] Eyesight
    Xp1, // [1X'] Mini Cross
    K1, // [1K] Knight
    Wp1, // [1W'] Longest Wall
    Ep1, // [1E'] Eyesight Difference
    X2, // [2X] Cross
    D2, // [2D] Deviation
    P2, // [2P] Product
    E2, // [2E] Encrypted
    M2, // [2M] Modulo
    A2, // [2A] Area
    L2, // [2L] Liar
    Xp2, // [2X'] Cross'
    I2, // [2I] Incomplete
    Ep2, // [2E'] Self-Referential
    Eh2, // [2E^] Double Encrypted
    Lp2, // [2L'] Liar'
    EL2,
    EX2,
    ED2,
    EM2,
    EA2,
    EP2,
    LX2,
    LD2,
    LM2,
    LA2,
    LP2,
}

export enum ClueState {
    Encrypted,
    Liar,
    NonLiar,
    EncryptedLiar,
    EncryptedNonLiar,
    SelfReferential,
    DoubleEncrypted,
}

export interface Clue {
    val: number[];
    type: ClueType;
    state?: ClueState;
    sqrt?: boolean;
}

export interface Cell {
    isFlag: boolean;
    open: boolean;
    clue: Clue | null;
}

export const parseCell = (desc: string): Cell => {
    // console.log('Parsing cell:', desc);
    const open = (desc !== desc.toLowerCase()); // if contains uppercase, it's given
    const type = desc.toLowerCase();
    if (type == 'f') {
        return { isFlag: true, open: false, clue: null };
    } else if (type == 'q') {
        return { isFlag: false, open: open, clue: null };
    } else if (type == 'qprior' || type == 'qx') {
        return { isFlag: false, open: true, clue: null };
    } else if (type == 'fx') {
        return { isFlag: true, open: true, clue: null };
    } else if (type == 'v-7') {
        return { isFlag: false, open: true, clue: { val: [7], type: ClueType.V } };
    } else {
        // split by digits, but ignore desc[0] even if it's a digit
        if (type[0] == 'v') {
            return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(1))], type: ClueType.V } };
        } else if (type[0] == '1') {
            if (type[1] == 'e') {
                return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(2))], type: ClueType.E1 } };
            } else if (type[1] == 'l') {
                return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(2))], type: ClueType.L1 } };
            } else if (type[1] == 'm') {
                return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(2))], type: ClueType.M1 } };
            } else if (type[1] == 'n') {
                return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(2))], type: ClueType.N1 } };
            } else if (type[1] == 'p') {
                return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(2))], type: ClueType.P1 } };
            } else if (type[1] == 'w') {
                const nums = type.slice(2).split('').map((c) => parseInt(c));
                return { isFlag: false, open: open, clue: { val: nums, type: ClueType.W1 } };
            } else if (type[1] == 'x') {
                return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(2))], type: ClueType.X1 } };
            }
        } else if (type[0] == '2') {
            if (type[1] == 'a') {
                return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(2))], type: ClueType.A2 } };
            } else if (type[1] == 'd') {
                return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(2))], type: ClueType.D2 } };
            } else if (type[1] == 'e') {
                if (type.length >= 4) {
                    if (type[2] == '\'') {
                        return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(3))], type: ClueType.Ep2, state: ClueState.SelfReferential } };
                    } else if (type[2] == 'a') {
                        return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(3))], type: ClueType.EA2, state: ClueState.Encrypted } };
                    } else if (type[2] == 'd') {
                        return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(3))], type: ClueType.ED2, state: ClueState.Encrypted } };
                    } else if (type[2] == 'l') {
                        if (type[3] == '-')
                            return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(4))], type: ClueType.EL2, state: ClueState.EncryptedLiar } };
                        else
                            return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(3))], type: ClueType.EL2, state: ClueState.EncryptedNonLiar } };
                    } else if (type[2] == 'm') {
                        return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(3))], type: ClueType.EM2, state: ClueState.Encrypted } };
                    } else if (type[2] == 'p') {
                        if (type.length >= 5)
                            return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(4))], type: ClueType.EP2, state: ClueState.Encrypted, sqrt: true } };
                        else
                            return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(3))], type: ClueType.EP2, state: ClueState.Encrypted } };
                    } else if (type[2] == 'x') {
                        const num = parseInt(type.slice(3));
                        return { isFlag: false, open: open, clue: { val: [num / 10, num % 10], type: ClueType.EX2, state: ClueState.Encrypted } };
                    } else if (type[2] == '^') {
                        return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(3))], type: ClueType.Eh2, state: ClueState.DoubleEncrypted } };
                    }
                } else {
                    return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(2))], type: ClueType.E2 } };
                }
            } else if (type[1] == 'i') {
                return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(2))], type: ClueType.I2 } };
            } else if (type[1] == 'l') {
                if (type[2] >= '0' && type[2] <= '9') {
                    return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(2))], type: ClueType.L2, state: ClueState.NonLiar } };
                } else if (type[2] == '-') {
                    return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(3))], type: ClueType.L2, state: ClueState.Liar } };
                } else {
                    if (type[2] == 'a') {
                        if (type[3] == '-')
                            return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(4)) - 1], type: ClueType.LA2, state: ClueState.Liar } };
                        else
                            return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(3))], type: ClueType.LA2, state: ClueState.NonLiar } };
                    } else if (type[2] == 'd') {
                        if (type[3] == '-')
                            return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(4)) - 1], type: ClueType.LD2, state: ClueState.Liar } };
                        else
                            return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(3))], type: ClueType.LD2, state: ClueState.NonLiar } };
                    } else if (type[2] == 'm') {
                        if (type[3] == '-')
                            return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(4)) - 1], type: ClueType.LM2, state: ClueState.Liar } };
                        else
                            return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(3))], type: ClueType.LM2, state: ClueState.NonLiar } };
                    } else if (type[2] == 'p') {
                        if (type[3] == '-')
                            return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(4))], type: ClueType.LP2, state: ClueState.Liar, sqrt: true } };
                        else
                            return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(3))], type: ClueType.LP2, state: ClueState.NonLiar, sqrt: true } };
                    } else if (type[2] == 'x') {
                        if (type[3] == '-') {
                            const num = parseInt(type.slice(4)) - 1;
                            return { isFlag: false, open: open, clue: { val: [num / 10, num % 10], type: ClueType.LX2, state: ClueState.Liar } };
                        } else {
                            return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(3,4)), parseInt(type.slice(4,5))], type: ClueType.LX2, state: ClueState.NonLiar } };
                        }
                    }
                }
            } else if (type[1] == 'm') {
                return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(2))], type: ClueType.M2 } };
            } else if (type[1] == 'p') {
                return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(2))], type: ClueType.P2, sqrt: true } };
            } else if (type[1] == 'x') {
                if (type[2] == '\'') {
                    return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(3))], type: ClueType.Xp2 } };
                } else {
                    return { isFlag: false, open: open, clue: { val: [parseInt(type.slice(2,3)), parseInt(type.slice(3,4))], type: ClueType.X2 } };
                }
            }
        }
    }
    console.log('Unknown cell type:', desc);
    return { isFlag: false, open: false, clue: null };
}

export class Board {
    c!: Cell[][];
    x!: number;
    y!: number;
    m!: number;
    r!: string;
    constructor(x: number, y: number, m: number, rules: string, cells?: string[]) {
        this.x = x;
        this.y = y;
        this.m = m;
        this.r = rules;
        this.c = new Array(x);
        if (cells) {
            for (let i = 0; i < x; i++) {
                this.c[i] = new Array(y);
                for (let j = 0; j < y; j++) {
                    this.c[i][j] = parseCell(cells[i * y + j]);
                }
            }
        } else {
            for (let i = 0; i < x; i++) {
                this.c[i] = new Array(y);
                for (let j = 0; j < y; j++) {
                    this.c[i][j] = { isFlag: false, open: false, clue: null };
                }
            }
        }
        console.log('Board created:', this);
    }
    get(x: number, y: number): Cell {
        return this.c[x][y];
    }
    set(x: number, y: number, cell: Cell) {
        this.c[x][y] = cell;
    }
}