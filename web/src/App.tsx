// App.tsx

import './App.css'

import { Board } from './definitions'

const App = () => {

    const puzzle = "f f f 2ld-3 2LA0 q q q f q 2lm-2 f f 2lm0 2l0 f q q q q f f f 2l3 2L-1 q q q q f 2lm2 2lm0 2lp-4 f q q q f q q 2LX00 2lx-02 2l1 q f q f q q q"
    const cells = puzzle.split(' ')
    const x = 5
    const y = 10
    const m = 10
    const r = ""
    const b = new Board(x, y, m, r, cells)

    return (
        <div className="App">
        <header className="App-header">
        </header>
            <p>
                Edit <code>App.tsx</code> and save to reload.
            </p>
            <a
                className="App-link"
                href="https://redwoodjs.com/"
                target="_blank"
                rel="noopener noreferrer"
            >
                Learn Redwood
            </a>
        </div>
    )
}

export default App