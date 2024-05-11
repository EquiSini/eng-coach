import { Component } from '@angular/core';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {

  myScriptElement: HTMLScriptElement;

  constructor() {
    this.myScriptElement = document.createElement("script");
    this.myScriptElement.src = "frontend/src/assets/yandexOauth.js";
    document.body.appendChild(this.myScriptElement);
  }




}
