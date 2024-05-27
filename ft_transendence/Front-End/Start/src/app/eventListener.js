////// debugger
const localhostPage = window.location.host;
//console.log("const localhostPage = window.location.host;  " + window.location.host);

//Home Page Settings Middle Button Save
//Validate Settings
Home._MiddleSettings?._Save?.addEventListener("click", async ()=>{
  //console.log("SAVE")
  if(!Home._MiddleSettings.isArgumentsEmpty())
    return
  if (!Home._MiddleSettings.checkPassword())
    return;
  if (!Home._MiddleSettings.checkValidEmail())
    return;
  await Home._MiddleSettings.changeData();
})
Home._MiddleSettings?._DeleteAccount.addEventListener("click",async ()=>{
  //console.log("_DeleteAccount")
  const deleteUser = await putRequest("DELETE", `api/v1/settings/${User._Id}`,{});
  myStorages.longOut();
})
//Home page Settings middle choose file for load image
// data:image/png;base64,
Home._MiddleSettings?._ImageFileAccess?.addEventListener("change", (event)=>{
  const file = event.target.files[0]; // Get the file
  const reader = new FileReader(); // Create a FileReader object
  // Closure to capture the file information.
  reader.onload = function(event) {
    //white Base64
    //console.log(event.target.result);
    base64EncodedImage = event.target.result + ""
    // Get the base64 encoded image data
    // <<data:image/png;base64,>> .length === 22
    base64EncodedImage  = base64EncodedImage.slice(22);
    if (base64EncodedImage[0] == ",")
      base64EncodedImage  = base64EncodedImage.slice(1);
    // You can now send the base64EncodedImage to the server via AJAX or any other method.
    //console.log(base64EncodedImage);
  };
  // Read in the image file as a data URL.
  reader.readAsDataURL(file);
})



// ProfileMidleHeaderToInvit
Home?._HomeMidleProfile?._ProfileMidleHeaderToInvit1?.addEventListener("click", async ()=>{

  ManageMidle.Manage("MidleHistoryGame");
})

Home?._HomeMidleProfile?._ProfileMidleHeaderToInvit2?.addEventListener("click",async ()=>{
  ManageMidle.Manage("MidleHistoryGame");
})
//JoinList Invite Button
// #JoinListHeroDivButtonBInvite
Home?._MidleJoinList?._InviteButton?.addEventListener("click",async ()=>{
  await ManageMidle.Manage("JoinListInvite");
})



Home._NAV._SETTINGS._classname?.addEventListener("click",()=>{
  ManageMidle.Manage("MidleSettings")
  NavigateHistoryALLITEM("/settings", localhostPage + '/settings', false)
})
Home?._NAV?._Home?._classname?.addEventListener("click",()=>{
  ManageMidle.Manage("midle");
  NavigateHistoryALLITEM("/midle", localhostPage + '/midle', false)
});

Home?._NAV?._Profile?._classname?.addEventListener("click", async ()=>{
  // debugger
  ManageMidle.Manage("ProfileMidle");
  NavigateHistoryALLITEM("/profil", localhostPage + '/profil', false);
})

Home?._NAV?._JoinListGame?._classname?.addEventListener("click",()=>{
  Join_Ws.send(JSON.stringify({
      "method": "get"
  }));
  ManageMidle.Manage("JoinList");
  NavigateHistoryALLITEM("/gamesa", localhostPage + '/gamesa', false);
})
// LEADERBOARD
Home?._NAV?._LEADERBOARD?._classname?.addEventListener("click",()=>{
  ManageMidle.Manage("MidleCub");
  NavigateHistoryALLITEM("/liderboard", localhostPage + '/liderboard', false);
} )
//  NavCommunity
Home?._NAV?._Community?._classname?.addEventListener("click",()=>{
  ManageMidle.Manage("MidleCommunity");
  NavigateHistoryALLITEM("/community", localhostPage + '/community', false);
} )
//whene create new list item for game
//_MidleJoinList Create button
Home._MidleJoinList?._CreateButton?.addEventListener("click", async () => {
    // //// debugger
  //console.log("click... \n");
  const Players = document.querySelector("#JoinListHeroDivProfilPlayers");
  const LiveOnOff = document.querySelector("#LiveOnOff");
  const JoinTheme = document.querySelector("#JoinTheme");
  const JoinListHeroDivGameMode = document.querySelector("#JoinListHeroDivGameMode");
  //console.log(Players.value);
  const objCreate = {
    max_players:Players.value,
    live:LiveOnOff.value,
    theme:JoinTheme.value,
    gamemode:JoinListHeroDivGameMode.value,
  };
  //send back-end
  // const url = "api/v1/createroom/" + User._Id;
  const paload = {
    "method": "create",
    "pk":User._Id,
    ...objCreate,
  }
  const str = JSON.stringify(paload)
  //   await FetchRequest("POST", url, objCreate);
  //redirect

  if (!Join_Ws)
    return;
  if (Join_Ws.readyState === WebSocket.OPEN) {
    //console.log('WebSocket connection is open 222222222222');
    Join_Ws.send(str);
  }
  //When Have Error
  Join_Ws.onclose = function (e) {
    //console.log("Something unexpected happened ! Join_Ws closed");
  };
  Players.value = "";
  LiveOnOff.value = "";
  JoinTheme.value = "";
  JoinListHeroDivGameMode.value = "";
})

Home._HomeLeft?._ExploreMessag?.addEventListener("click",  ()=>{
  if (!User.checkSignIn())
    return;

  const style = Home._HomeMessage?._style;
  //console.log("d.display == " + style.display)
  const flag = style.display == "none" ? "block" : "none";
  if (flag == "block")
  {
    ManageRight.Manage("Message");
  }
  else
    style.display = "none";
})
//-------------------------------------------------------------------- left User
// IconExit
Home._HomeLeft._LongOut.addEventListener("click", async () => {
  myStorages.longOut();
  await ManageAllPage.Manage("Home");
  await  NavigateHistoryALLITEM("/", localhostPage + '/', false)
})

Home._HomeLeft._NavLoginOut.addEventListener("click", async () => {
  myStorages.longOut();
  await ManageAllPage.Manage("Home");
  await  NavigateHistoryALLITEM("/", localhostPage + '/', false)
})
//---------------------------------------------------------------------   Login
//when want to login you press button login
Login?._LoginPageContinue?.addEventListener("click", async (e) =>  {
// ////// debugger
  e.preventDefault();
  //check is correct email and password
  if (Login.ButtonSignIn())
  {
    //code random 10 numbers
    const hash = HashCodeGeneration();
    User._Email = Login._LoginEmail.value;
    //respons beck-end to tack user
    const data =  await FetchRequest("POST", "login", {"email":Login._LoginEmail.value, "password" : hash + Login._LoginPassword.value + hash})
    //error div innerHTML =""
    Password.errorSetNull();

    if (data.state)
    {
      if (data?.message?.twoFA)
      {
        // Confirm.setDisplayBlock(Home);
        ManageAllPage.Manage("Confirm");
        await  NavigateHistoryALLITEM("/confirm", localhostPage + '/confirm', false);
        return;
      }
      //set local storage data access and refresh tokin
      myStorages.setStorageLogin(data?.message?.data)
      if (User.checkSignIn())
      {
        const SignInButton = document.querySelector(".LoginPageContinue");
        SignInButton.setAttribute("href", "/");
        await ManageAllPage.Manage("Home");
        await  NavigateHistoryALLITEM("/", localhostPage + '/', false)
        Login._LoginEmail.value = "";
        Login._LoginPassword.value = "";
      }
    }
    else{
      //set error in frontend
      Password.notFined();
    }
  }
})
// when forgot password
// Login?._LoginPageForgot?.addEventListener("click", async (e) => {
//   //// debugger
// e.preventDefault();
//   await ManageAllPage.Manage("ResetPage");
//   await  NavigateHistoryALLITEM("/reset", localhostPage + '/reset', false)
//   ManageMidle.Manage("");
// })
//-------------------------------------------------------------------  Reset
let isReset = false;
Reset?._ConfirmReset?.addEventListener('click', async () => {
    ////// debugger
  const isValid = Reset.checkValidEmail();
  if (!isValid)
    return ;
  const res = await Reset.ResetEmail();
  if (!res)
    return ;
  ManageAllPage.Manage("Confirm");
  await  NavigateHistoryALLITEM("/confirm", localhostPage + '/confirm', false);

  isReset = true;
})
//-------------------------------------------------------------------  Confirm  ---------
Confirm.ConfirmYourEmail.addEventListener('click', async () => {
    ////// debugger
  const data = await Confirm.ConfirmPageContinue(isReset);
  Confirm.ValuesAllEmpty();
  //console.log("isReset    " + isReset);
  //when came this page in Reset Password page
  if (isReset)
  {
    ManageAllPage.Manage("Confirm");
    await  NavigateHistoryALLITEM("/confirm", localhostPage + '/confirm', false);
    if (!data || !data.state)
    { 
      await ManageAllPage.Manage("ResetPage");
      await  NavigateHistoryALLITEM("/reset", localhostPage + '/reset', false)
      return ;
    }
    User._ConfirmEmail = true;
    await ManageAllPage.Manage("Password");     //go to password page for create new password
    await  NavigateHistoryALLITEM("/password", localhostPage + '/password', false)
    return ;
  }
  //console.log("    data == " + JSON.stringify(data));
  //when came this page Welcome to ft_transcendence
  if (!data) {
    User._ConfirmEmail = false;
  }
  else if (data.state) {
    if (data?.message?.twoFA)//----------------------------------------------------------
    {
      if (data.message.data)
        myStorages.setStorageLogin(data?.message?.data)
      ManageMidle.Manage("midle");
      await ManageAllPage.Manage("Home")
      await  NavigateHistoryALLITEM("/", localhostPage + '/', false)
      return;
    }
    User._ConfirmEmail = true;
    Confirm.DisplayNone();
    await SignUp.DisplayBlock();
    await  NavigateHistoryALLITEM("/setdata", localhostPage + '/setdata', false)
  }
  else if (data.message.substr(-3) == "408") {
    User._ConfirmEmail = false;
    ManageMidle.Manage("midle");
    await ManageAllPage.Manage("Home")
    await  NavigateHistoryALLITEM("/", localhostPage + '/', false)
  }
  isReset = false;
})
//-------------------------------------------------------------------  Password
Password.PasswordConfirm.addEventListener("click", async () => {
    // //// debugger
  const isCorrectPassword = Password.PasswordConfirmButton();
  if (isCorrectPassword)
  {
    const codeSesion = await Password.PasswordConfirmWithServer();
    //console.log("codeSesion = " + codeSesion + " typeof(codeSesion) " + typeof(codeSesion));
    
    if (codeSesion.state)
    {
      myStorages.longOut();
      await ManageAllPage.Manage("Login");
      await  NavigateHistoryALLITEM("/login", localhostPage + '/login', false)
    }
  }
})
//-------------------------------------------------------------------  SignUp
SignUp.SignupPageContinue.addEventListener("click", async () => {
    // //// debugger
  const isCorrectPassword = SignUp.PasswordConfirmButton();
  const ischeckNameNickname = SignUp.checkNameNickname();
  const errorNickname = document.querySelector(".SignupPageinputDivErrorNickname");
  errorNickname.innerHTML = "";

  if (isCorrectPassword && ischeckNameNickname) {
   const codeSesion = await SignUp.PasswordConfirmWithServer();
   //console.log(codeSesion);
    if (codeSesion.state) {
      SignUp.DisplayNone();
      Login.DisplayBlock();
      await  NavigateHistoryALLITEM("/login", localhostPage + '/login', false)
    }
    else {
      const status = codeSesion.message.slice(codeSesion.message.length - 3)
      if (status == "409") {
      errorNickname.innerHTML = "nickname already used";
      errorNickname.style.color = "red";
      }
    }
  }
})
//RegisterPage click confirm email
Register?._RegisterPageContinue?.addEventListener("click",  async () => {
    // //// debugger
      let value = await Register.RegistersWithEmail();
      if (value) {
        Register.RegisterPageDisplayNone();
        ManageAllPage.Manage("Confirm");
        await  NavigateHistoryALLITEM("/confirm", localhostPage + '/confirm', false);
      }
});



//42 registration
Login?._ContinueWith42Intra?.addEventListener("click", async () => {
  const respons =  await Login.Get42Connect();
})

Register?._ContinueWith42Intra?.addEventListener("click", async () => {
  const respons = await Register.Get42Connect();
})



//play game local
local_game?.playNow?.addEventListener("click", async () =>{


  await ManageMidle.Manage("");
  await ManageAllPage.Manage("local_game");
  await  NavigateHistoryALLITEM("/local_game", localhostPage + '/local_game', false)
  const mainOnHtml = document.querySelector("#mainSectionUsually");
  
  mainOnHtml.style.display = "none";
})
