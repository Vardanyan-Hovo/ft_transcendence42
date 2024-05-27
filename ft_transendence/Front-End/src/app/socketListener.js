var Join_Ws = new WebSocket("ws://" + HostPort.slice(7) + "/ws/joinlist/")

var isStartedUrish = false;

console.log("HostPort.slice(7) =" + HostPort.slice(7))
Join_Ws.onmessage = message => {
    if (!message.data)
        return;
    let response = JSON.parse(message.data);
    // console.log(JSON.stringify(response))
    //update Join list items
    if (response.method === "join_list_room" && User._getAccess) {
        Home._MidleJoinList._game_rooms = response.game_rooms;
        const join_listButton = document.querySelector(".JoinList");
        if (join_listButton.style.display !== "none")
            ManageMidle.Manage("JoinList");
    }

    if (response.method === "updateLiveGames" && User._getAccess) {
        console.log("response = ", response);
        console.log("User._Id = ", User._Id);
        console.log("isStartedUrish = ", isStartedUrish);
        response.liveGames.forEach(async element => {
            if (isStartedUrish === false && (User._Id == element.game_room.left_id || User._Id == element.game_room.right_id)) {
                //main displey none
                const mainOnHtml = document.getElementById("mainSectionUsually");
                const body = document.querySelector(".addBodyStile");

                mainOnHtml.style.display = "none";
    //add game
                if (document.getElementById("board")){
                    body.innerHTML = null;
                }
                const gameOnHtml = document.createElement("div");
                gameOnHtml.setAttribute("id", "board")
                body.style.display = "block";
                body.appendChild(gameOnHtml)
    // }
                //call game function for start game
                isStartedUrish = true;
                pongGame(User, element.game_room.room_id, "connect");
            }
        });
    }
}
