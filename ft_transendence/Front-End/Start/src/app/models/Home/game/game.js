// import {PongGame} from "./pongGame.js";

// var gameInstance = new PongGame();
let interval = null;
// function disableScrolling(){
//     var x=window.scrollX;
//     var y=window.scrollY;
//     window.onscroll=function(){window.scrollTo(x, y);};
// }

// function enableScrolling(){
//     window.onscroll=function(){};
// }

// var arrow_keys_handler = function(e) {
//     switch(e.code){
//         case "ArrowUp": case "ArrowDown": case "ArrowLeft": case "ArrowRight": 
//             case "Space": e.preventDefault(); break;
//         default: break; // do not block other keys
//     }
// };

function waitingKeypress() {
    return new Promise((resolve) => {
        document.addEventListener('keydown', onKeyHandler);
        function onKeyHandler(e) {
            if (true) {
                document.removeEventListener('keydown', onKeyHandler);
                resolve();
            }
        }
    });
}

function disableScroll() {
    // Get the current page scroll position in the vertical direction
    scrollTop =
        window.pageYOffset || document.documentElement.scrollTop;
        
        
    // Get the current page scroll position in the horizontal direction 

    scrollLeft =
    window.pageXOffset || document.documentElement.scrollLeft;


    // if any scroll is attempted,
    // set this to the previous value
    window.onscroll = function() {
    window.scrollTo(scrollLeft, scrollTop);
    };
}

function enableScroll() {
    // debugger
    window.onscroll = function() {};
}

function pongGame(objUser, gameRoom, mode) {
    const gameid = gameRoom.room_id;
    let isStarted = false;

    disableScroll();
    function isOpen(ws) { return ws.readyState === ws.OPEN }
    //HTML elements
    let clientId = objUser._Id;
    let paddleName = null;
    const constants = {
        "paddle_step": null,
        "screen_width": null,
        "screen_height": null
    }
    // let paddle_step = null;
    // let screen_width = null;
    // let screen_height = null;
    if (!clientId)
        clientId = uuid();
    let gameId = gameid;
    // let ws = new WebSocket("ws://" + window.location.host + "/ws/game/" + gameId)

//++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ws = new WebSocket("ws://" + HostPort.slice(7) + "/ws/game/" + gameId)

//++++++++++++++++++++++++++++++++++++++++++++++++++++++

    const payLoad = {
        "method": mode,
        "clientId": clientId,
        "gameId": gameId
    }

    ws.onopen = () => ws.send(JSON.stringify(payLoad));
    console.log("ws://" + window.location.host + "/ws/game/");
    console.log("ws = ", window.location.host);
    const board = document.getElementById("board");

    clearBox("board");
    //wiring events
    document.addEventListener("keydown", event => {
        // console.log(event);
        // if (gameId === null)
        //     return ;
        const payLoad = {
            "method": "updateKey",
            "clientId": clientId,
            "gameId": gameId
        }
        // console.log("paddleName = ", paddleName);
        if (event.key === "ArrowUp") {
            payLoad["direction"] = "up";
        }
        else if (event.key === "ArrowDown") {
            payLoad["direction"] = "down";
        }
        else
            return;
        if (ws.readyState === ws.OPEN) {
            ws.send(JSON.stringify(payLoad));
        }
    });

    function clearBox(elementID) {
        document.getElementById(elementID).innerHTML = "";
    }

    ws.onmessage = async message => {
        //message.data
        // console.log("✅ message = ", message);
        let response;
        if (message) {
            try {
                response = JSON.parse(message.data);
            }
            catch (e) {
                console.log("e = ", e);
                return console.error(e);
            }
        }
        console.log("response method = ", response.method);
        const mainOnHtml = document.getElementById("mainSectionUsually");
        const body = document.querySelector(".addBodyStile");

        if (response?.method === "finish_match" && User?._getAccess) {
            const resultText = document.getElementById('result');
            const forStart = document.getElementById("forStart");

            forStart.style.display = "none";
            
            console.log("response?.state?.game_room = ", response?.state?.game_room);
            console.log("response?.state?.game_room = ", response?.state?.game_room);
            if (mode == "view")
                resultText.innerHTML = response?.state?.game_room?.winner + " won the game";
            else if (response?.state?.game_room?.winner == clientId)
                resultText.innerHTML = 'you won';
            else
                resultText.innerHTML = 'you lost';
            resultText.style.display = 'block';
            await new Promise(resolve => setTimeout(resolve, 3000));
            clearInterval(interval);
            ws.close();
            clearBox("board");
            // update when game terminate
            mainOnHtml.style.display = "block";
            body.style.display = "none";
            enableScroll();
            isStarted = false;
            isStartedUrish = false;
            await Join_Ws.send(JSON.stringify({"method": "updateLiveGames"}));
            document.querySelector("body").style.overflow = "unset";
            return
        }
        if (response.method === "connect"){
            console.log("response = ", response);
            paddleName = response.state[clientId];
            // clientId = response.clientId;
            constants.paddle_step = response.constants.paddle_step;
            constants.screen_width = response.constants.screen_width;
            constants.screen_height = response.constants.screen_height;
            console.log("Client id Set successfully " + clientId)
            if (isStarted === false) {
                isStarted = true;
                board.innerHTML = getPongContent();
                document.querySelector("body").style.overflow = "hidden";
                // await new Promise(resolve => setTimeout(resolve, 5000));
            }
            const username1 = document.getElementById("username1");
            const username2 = document.getElementById("username2");

            username1.textContent = gameRoom.left_name;
            username2.textContent = gameRoom.right_name;
            // if (paddleName === "paddle1") {
            //     const usnername = getElementById("username1");
            //     usnername.textContent = response.state.paddle1.username;
            // } else if (paddleName === "paddle2") {
            //     const usnername = getElementById("username2");
            //     usnername.textContent = response.state.paddle2.username;
            // }
            if (mode != "view") {
                const forStart = document.getElementById("forStart");
                forStart.style.display = "block";
                await waitingKeypress();
                forStart.style.display = "none";
                if (ws.readyState === ws.OPEN)
                    ws.send(JSON.stringify({"method": "ready"}));
            }
            interval = setInterval(() => {
                try {
                    if (ws.readyState === ws.OPEN)
                        ws.send(JSON.stringify({"method": "no_action"}));
                }catch (e) {
                    clearInterval(interval);
                }
            }, 10);

        }
        //create
        if (response.method === "create"){
            console.log("response = ", response);
            gameId = response.game["id"];
            console.log("game successfully created with id " + response.game.id + " with " + response.game.balls + " balls")  
        }
        //update
        if (response.method === "update"){
            if (!response.state)
                return;
            const ballObject = document.getElementById("ball");
            // ballRadius = response.state.ballRadius;
            if (!response?.state?.ball?.x || !response?.state?.ball?.y)
                return
            ballObject.style.left = response?.state?.ball?.x + "px";
            ballObject.style.top = response?.state?.ball?.y + "px";
            // console.log("response.state.paddle2 = ",response.state.paddle2)
            // console.log("response.state.paddle1 = ",response.state.paddle1)
            // console.log("paddleName = ", paddleName);
            // if (paddleName === "paddle1") {
                const paddle1 = document.getElementById("paddle1");
                paddle1.style.left = response.state.paddle1.x + "px";
                paddle1.style.top = response.state.paddle1.y + "px";
                // console.log("paddle1.style.left = ", paddle1.style.left);
                // console.log("paddle1.style.top = ", paddle1.style.top);
            // }
            // else if (paddleName === "paddle2") {
                const paddle2 = document.getElementById("paddle2");
                paddle2.style.left = response.state.paddle2.x + "px";
                paddle2.style.top = response.state.paddle2.y + "px";
                // console.log("paddle2.style.left = ", paddle2.style.left);
                // console.log("paddle2.style.top = ", paddle2.style.top);
            // }
            const score1 = document.getElementById("score1");
            const score2 = document.getElementById("score2");
            score1.textContent = response.state.paddle1.score;
            score2.textContent = response.state.paddle2.score;
        }
        //join
        // if (response.method === "join") {
        //     board.innerHTML = getPongContent();
            
        // }
    }
}

// export {pongGamelol};

function getPongContent() {
    return `
    <div id="paddle1" class="paddle" style="width: 20px; height: 100px; left: 0px; top: 200px;"></div>
    <div id="paddle2" class="paddle" style="width: 20px; height: 100px; left: 680px; top: 200px;"></div>
    <div class="ball" id="ball" style="width: 14px; height: 14px; border-radius: 30px; left: 350px; top: 250px;"></div>
    <span id="result" style="display: none">default</span>
    <span id="forStart" style="display: none">Press any key to start</span>
    <span class="score" id="score1">0</span>
    <span class="score" id="score2">0</span>
    <span class="username1" id="username1">username1</span>
    <span class="username2" id="username2">username2</span>
    `;
}