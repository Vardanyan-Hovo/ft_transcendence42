const friend = {
  url:"../../../public/Grup2.png",
  name : "Karen Hakobyan"
}
const body = {
  image:"../../../public/Grup2.png",
  name : "Karen Hakobyan"
}

class MidleProfile extends HtmlElement {
    constructor(){
      super(".ProfileMidle")
      this._style.display = "none";
    }
    _ProfileMidleHeaderToInvit1 = document.querySelector("#ProfileMidleHeaderToInvit1");
    _ProfileMidleHeaderToInvit2 = document.querySelector("#ProfileMidleHeaderToInvit2");
    _ProfileMidleFooterDiv  = document.querySelector(".ProfileMidleFooterDiv");
    _ProfileMidleBodyItems = document.querySelector(".ProfileMidleBodyItems");

    async addEventListenerAcceptOrReject(className){
      const nodsAcceptsOrRejects = document.querySelectorAll(className);

      nodsAcceptsOrRejects.forEach(async (button) => {
        button.addEventListener("click", async (e) => {
          //tack id
          const id = e.target.id.slice(e.target.id.lastIndexOf(':') + 1)
          
          //create data
          const sendFrend = {
            // "method" : "invite",
            sender_id: id
          }
          // Join_Ws.send(JSON.stringify(sendFrend));
          AcceptRejectAccept:2
          if (className == ".AcceptRejectAccept") {
            // path('api/v1/accept/<int:pk>/', AcceptFriendRequest.as_view()),  
            let friendAdd;
            if (e.target.innerHTML == "Join")
            {
              // debugger
              friendAdd = await putRequest("POST", "api/v1/acceptinvite/" + User._Id, sendFrend)
              if (friendAdd?.state)
              {
                Join_Ws.send(JSON.stringify({
                  "method": "no_action"
                }));
              }
            }
            else
              friendAdd = await putRequest("POST", "api/v1/accept/" + User._Id, sendFrend)

            if (!friendAdd.state)
              return;
          }
          else {
            // path('api/v1/reject/<int:pk>/', RejectFriendRequest.as_view()),
            let friendAdd;
            if (e.target.innerHTML == "Ignore")
              friendAdd = await putRequest("POST", "api/v1/rejectinvite/" + User._Id, sendFrend)
            else
              friendAdd = await putRequest("POST", "api/v1/reject/" + User._Id, sendFrend)
            if (!friendAdd.state)
              return;
          }
          ManageMidle.Manage("ProfileMidle");
         
        })
      })
    }
/* 
  1<div class="ProfileMidleFooterUser">
    <img src="../../../public/Grup2.png" alt="Friends" class="ProfileMidleFooterUserImage">
    <p class="ProfileMidleFooterUserName">User1</p>
  </div> 
*/
    profilHeader(){
      document.querySelector("#ProfileMidleHeaderMainAvatarImage").src = `data:image/png;base64,${User._Image}`;
      document.querySelector(".ProfileMidleHeaderMainDataName").innerHTML = User._Name;
      document.querySelector(".ProfileMidleHeaderMainDataNickName").innerHTML = User._Nickname;
      document.querySelector("#ProfileMidleHeaderToInvit1id1").innerHTML = User._WinCount || 0;
      document.querySelector("#ProfileMidleHeaderToInvit2id2").innerHTML = User._LoseCount || 0;

      this._ProfileMidleFooterDiv.innerHTML = "";
      this._ProfileMidleBodyItems.innerHTML = "";
    }
  //who wants to be added to your friends list
  // 1<div class="ProfileMidleBodyItem">
  // 2  <div class="ProfileMidleBodyItemConteiner">
  //      2_1  <div class="ProfileMidleBodyImage">
  //              <img src="../../../public/conva.png" class="ProfileMidleBodyUserImage"
  //                    width="30" height="30" alt="Invite"  />
  //           </div>
  //      2_2  <p class="ProfileMidleBodyUser">
  //              User1
  //           </p>
  //      2_3  <div class="AcceptReject">
  //              2_Accept      <div class="AcceptRejectAccept">
  //                              Accept
  //                            </div>
  //               2_Reject     <div class="AcceptRejectReject">
  //                                Reject
  //                            </div>
  //          </div>                                            
  //   </div>
  // </div>
  // Request for Accept Ignore
    profilBody(Item, Request){
      const div1 = document.createElement("div");
      div1.setAttribute("class","ProfileMidleBodyItem");

      const div2 = document.createElement("div");
      div2.setAttribute("class","ProfileMidleBodyItemConteiner");

      const div2_1 = document.createElement("div");
      div2_1.setAttribute("class","ProfileMidleBodyImage");
      const div2img = document.createElement("img");
      div2img.setAttribute("class", "ProfileMidleBodyUserImage");
      div2img.setAttribute("src", `data:image/png;base64,${Item.image}`);
      div2img.setAttribute("width","30");
      div2img.setAttribute("height", "30");
      div2img.setAttribute("alt", "Invite");
      div2_1.appendChild(div2img);
      div2.appendChild(div2_1);

      const div2_2 = document.createElement("p");
      div2_2.setAttribute("class", "ProfileMidleBodyUser");
      div2_2.innerHTML = Item.name;
      div2.appendChild(div2_2);
      const div2_3 = document.createElement("div");

      div2_3.setAttribute("class", "AcceptReject");
      
      const div2_Accept = document.createElement("div");
      div2_Accept.setAttribute("class","AcceptRejectAccept");
      div2_Accept.setAttribute("id","AcceptRejectAccept:"+Item.id);
      if (Request == "FriendRequest")
        div2_Accept.innerHTML = "Accept";
      else
        div2_Accept.innerHTML = "Join";
      const div2_Reject = document.createElement("div");
      div2_Reject.setAttribute("class", "AcceptRejectReject")
      div2_Reject.setAttribute("id", "AcceptRejectReject:"+ Item.id)

      if (Request == "FriendRequest")
        div2_Reject.innerHTML = "Reject";
      else
        div2_Reject.innerHTML = "Ignore";
      
      div2_3.appendChild(div2_Accept);
      div2_3.appendChild(div2_Reject);
      div2.appendChild(div2_3);

      div1.appendChild(div2);
    
      this._ProfileMidleBodyItems.appendChild(div1);
    }
// Friends list
    frendsdrawScreen(friend){
      const divProf = document.createElement("div");
      divProf.setAttribute("class", "ProfileMidleFooterUser");
      const img = document.createElement("img");
      img.setAttribute("class","ProfileMidleFooterUserImage");
      img.setAttribute("alt", "Friends");
      img.setAttribute("id", `Friends${friend.id}id`);
      img.setAttribute("src", `data:image/png;base64,${friend.image}`);
      const p = document.createElement("div");
      p.setAttribute("class", "ProfileMidleFooterUserName");
      p.innerHTML = friend.nickname;
      divProf.appendChild(img);
      divProf.appendChild(p);

      this._ProfileMidleFooterDiv.appendChild(divProf);
    }
    async getFriends(){
      // ////// debugger
      this.profilHeader();
      const users = await getFetchRequest("users");
      // Of all the users, only my data was taken
      const UserData = users.message.find((e)=>e.id == User._Id);
      const friendship_requests = UserData.friendship_requests;
      const gameinvite_requests = UserData.gameinvite_requests;

      if (friendship_requests) {
        // //// debugger
        friendship_requests.forEach((item)=>{
          if (!item.rejected)
          this.profilBody(item, "FriendRequest");
        })
      }
      if (gameinvite_requests) {
          // //// debugger
          gameinvite_requests.forEach((item) => {
            if (!item.rejected)
            this.profilBody(item, "JoinRequest");
          })
        //event listener in to friendship requests Accept
        this.addEventListenerAcceptOrReject(".AcceptRejectAccept");
        //event listener in to friendship requests Reject
        this.addEventListenerAcceptOrReject(".AcceptRejectReject");
      }
      const friends = await getFetchRequest("api/v1/friendlist/" + User._Id);
      if (friends && friends.state) {
        friends.message.friends.forEach(async item => {
          this.frendsdrawScreen(item);
        });
      }
    }
    async draw(){
      // //// debugger
      await this.getFriends();
    }
}



// fields = ('id', 'name', 'nickname', 'email', 'image', 'phone', 'wins', 'loses', 'matches',
//                 'points', 'gamemode', 'live', 'is_online', 'friends', 'friendship_requests', 'gameinvite_requests')