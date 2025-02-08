function myfunc() {
    let a = document.getElementById('a');
    let d = 0;
    a.innerHTML = ``;
    for (let i = 0; i < 8; i++) {
        let c = "";
        for (let j = 0; j < 8; j++) {
            let b = (d % 2 === 0) ? "green" : "white";
            c += `<td style="background-color:${b}" data-original-color="${b}" onclick="resetBoard();"></td>`;
            d++;
        }
        a.innerHTML += `<tr>${c}</tr>`;
        d = (i % 2 === 0) ? 1 : 0;
    }
    let b = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'];
    let c = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'];
    for (let i = 1; i < 9; i++) {
        insertImage(1, i, "image 1/" + b[i - 1] + ".png");
        insertImage(8, i, "image 2/" + c[i - 1] + ".png");
        insertImage(2, i, "image 1/p.png");
        insertImage(7, i, "image 2/P.png");
    }
}

function insertImage(row, col, imagePath) {
    let table = document.getElementById('a');
    let selectedrow = table.rows[row - 1];
    let selectedCell = selectedrow.cells[col - 1];
    
    if (!selectedCell.querySelector("img")) {
        let img = document.createElement("img");
        img.src = imagePath;
        img.style.width = "50px";
        img.style.height = "50px";
        img.setAttribute("data-piece", imagePath.split("/").pop().split(".")[0]);
        
        img.onclick = function (event) {
            event.stopPropagation();
            resetBoard();
            let clickedCell = event.target.closest('td');
            let clickedRow = clickedCell.parentNode.rowIndex;
            let clickedCol = clickedCell.cellIndex;
            highlightCell(clickedCell, clickedRow, clickedCol, img.getAttribute("data-piece"));
        };
        
        selectedCell.appendChild(img);
    }
}

function removeImage(row, col) {
    let table = document.getElementById('a');
    let selectedrow = table.rows[row - 1];
    let selectedCell = selectedrow.cells[col - 1];
    let existingImage = selectedCell.querySelector("img");
    if (existingImage) {
        selectedCell.removeChild(existingImage);
        return existingImage;
    }
    return null;
}

function resetBoard() {
    let cells = document.querySelectorAll("#a td");
    cells.forEach(cell => {
        cell.style.backgroundColor = cell.getAttribute('data-original-color');
        let dot = cell.querySelector(".dot");
        if (dot) dot.remove();
    });
}

function highlightCell(cell, row, col, piece) {
    resetBoard(); 
    if (cell.querySelector("img")) {
        cell.style.backgroundColor = "yellow";
        getPossibleMoves(cell, row, col, piece);
    }
}

function getPossibleMoves(cell, row, col, piece) {
    let table = document.getElementById('a');
    const directions = {
        rook: [[1, 0], [-1, 0], [0, 1], [0, -1]],
        bishop: [[1, 1], [-1, -1], [1, -1], [-1, 1]],
        queen: [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, -1], [1, -1], [-1, 1]],
        knight: [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [1, -2], [-1, 2], [-1, -2]],
        king: [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, -1], [1, -1], [-1, 1]]
    };

    function addMoves(directions, repeat) {
        for (let [dr, dc] of directions) {
            let r = row, c = col;
            while (true) {
                r += dr;
                c += dc;
                if (r < 0 || r >= 8 || c < 0 || c >= 8) break;
                let targetCell = table.rows[r].cells[c];
                let targetPiece = targetCell.querySelector("img") ? targetCell.querySelector("img").getAttribute("data-piece") : null;
                if (targetPiece) { 
                    if ((piece === piece.toUpperCase() && targetPiece === targetPiece.toUpperCase()) || 
                        (piece === piece.toLowerCase() && targetPiece === targetPiece.toLowerCase())) {
                        break;
                    }
                    placeRedDot(row, col, targetCell);
                    break;
                }
                placeRedDot(row, col, targetCell);
                if (!repeat) break;
            }
        }
    }

    if (piece === 'Q' || piece === 'q') addMoves(directions.queen, true);
    else if (piece === 'R' || piece === 'r') addMoves(directions.rook, true);
    else if (piece === 'B' || piece === 'b') addMoves(directions.bishop, true);
    else if (piece === 'N' || piece === 'n') addMoves(directions.knight, false);
    else if (piece === 'K' || piece === 'k') {
        addMoves(directions.king, false);
    }
    else if (piece === 'P' || piece === 'p') {
        let forward = (piece === 'P') ? -1 : 1; 
        let startRow = (piece === 'P') ? 6 : 1;
        let enPassantRow = (piece === 'P') ? 3 : 4;
        if (row + forward >= 0 && row + forward < 8) {
            let targetCell = table.rows[row + forward].cells[col];
            if (!targetCell.querySelector("img")) {
                placeRedDot(row, col, targetCell);
                if (row === startRow) { 
                    let doubleMove = table.rows[row + 2 * forward].cells[col];
                    if (!doubleMove.querySelector("img")) {
                        placeRedDot(row, col, doubleMove);
                    }
                }
            }
        }
        for (let dc of [-1, 1]) {
            let captureRow = row + forward;
            let captureCol = col + dc;
            if (captureRow >= 0 && captureRow < 8 && captureCol >= 0 && captureCol < 8) {
                let captureCell = table.rows[captureRow].cells[captureCol];
                let targetPiece = captureCell.querySelector("img") ? captureCell.querySelector("img").getAttribute("data-piece") : null;
                if (targetPiece && ((piece === 'P' && targetPiece === targetPiece.toLowerCase()) || (piece === 'p' && targetPiece === targetPiece.toUpperCase()))) {
                    placeRedDot(row, col, captureCell);
                }
            }
        }
        if (row === enPassantRow) {
            for (let dc of [-1, 1]) {
                let sideCol = col + dc;
                if (sideCol >= 0 && sideCol < 8) {
                    let sideCell = table.rows[row].cells[sideCol];
                    let sidePiece = sideCell.querySelector("img") ? sideCell.querySelector("img").getAttribute("data-piece") : null;
                    if (sidePiece && ((piece === 'P' && sidePiece === 'p') || (piece === 'p' && sidePiece === 'P'))) {
                        let enPassantCell = table.rows[row + forward].cells[sideCol];
                        placeRedDot(row, col, enPassantCell);
                    }
                }
            }
        }
    }
}

function placeRedDot(row, col, cell) {
    let dot = document.createElement("div");
    dot.className = "dot";
    cell.style.position = "relative";
    cell.appendChild(dot);
    dot.onclick = function (event) {
        event.stopPropagation();
        movePiece(row, col, cell);
    };
}

function movePiece(row, col, targetCell) {
    let table = document.getElementById('a');
    let selectedRow = table.rows[row];
    let selectedCell = selectedRow.cells[col];
    let img = selectedCell.querySelector('img');
    if (img) {
        let existingImg = targetCell.querySelector('img');
        if (existingImg) {
            targetCell.removeChild(existingImg);
        }
        targetCell.appendChild(img);
        resetBoard();
    }
}

function bestmove(event) {
    let turn = event.target.getAttribute("val");
    console.log("Button Clicked, Turn:", turn);  // Debugging line

    fetch("https://chess-lgwl.onrender.com/get_best_move", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ turn: turn })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Response Data:", data); // Debugging response

        if (data.error) {
            console.error("Error:", data.error);
            return;
        }

        let startRow = data.start_row - 1; 
        let startCol = data.start_col - 1;
        let endRow = data.end_row - 1;
        let endCol = data.end_col - 1;
        
        document.getElementById('k').innerText=`${String.fromCharCode(97 + startCol)}${8 - startRow} to ${String.fromCharCode(97 + endCol)}${8 - endRow}`;
        
        movePiece(startRow, startCol, document.getElementById("a").rows[endRow].cells[endCol]);
    })
    .catch(error => console.error("Error:", error));
}
