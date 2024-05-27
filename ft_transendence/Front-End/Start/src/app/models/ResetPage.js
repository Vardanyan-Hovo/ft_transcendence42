//Reset Page
class ResetPageA extends HtmlElement {
  constructor() {
    super(".ResetPage");
    this._style.display = "none";
  }
  _ConfirmReset = document.querySelector(".ResetPageContinue");
  _Email = document.querySelector(".ResetPageinput");                      //input Email
  _ErrorEmail = document.querySelector(".ResetPageEmailError");             //when email is not correct

  checkValidEmail() {
    this._ErrorEmail.innerHTML = "";
    this._ErrorEmail.style.color = "red";
    if (!this._Email || !this._Email.value) {
      this._ErrorEmail.innerHTML = "Email cannot be empty";
      return false;
    }
    const respons =  ValidateEmail(this._Email.value);
    if (!respons || respons[0] !== "V") {
      this._ErrorEmail.innerHTML = "Email is not correct";
      return false
    }
    User._Email = this._Email.value;
    return true;
  }

  async ResetEmail() {
    this._ErrorEmail.innerHTML = "";
    this._ErrorEmail.style.color = "red";
  
    if (!this._Email || !this._Email.value) {
      this._ErrorEmail.innerHTML = "Email cannot be empty";
      return false;
    }
    const res = await FetchRequest("POST", "password_reset", {email:this._Email.value});
    if (!res.state) {
      this._ErrorEmail.innerHTML = "Email is not correct";
      return false
    }
    return true;
  }
  draw(){}
}
  