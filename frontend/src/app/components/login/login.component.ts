import {Component, inject} from '@angular/core';
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {Router} from "@angular/router";
import {environment} from "../../../environments/environment";
import {LoginService} from "../../services/login.service";

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, ReactiveFormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {

router = inject(Router);
loginService = inject(LoginService);

  // loginWithGoogle() {
  //
  //   const clientId: string = environment.GOOGLE_CLIENT_ID;
  //   const redirectUri: string = 'http://localhost/googleOauth2callback';
  //   const responseType: string = 'code';
  //   const scope: string = 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile';
  //   const includeGrantedScopes: string = 'true';
  //   const state: string = 'pass-through value';
  //
  //   window.location.href = encodeURI(`https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=${responseType}&scope=${scope}&include_granted_scopes=${includeGrantedScopes}&state=${state}`)
  // }

  // loginWithYandex() {
  //
  //   const clientId: string = environment.YANDEX_CLIENT_ID;
  //   const redirectUri : string = 'http://localhost/yandexOauth2callback';
  //   const responseType: string = 'code'
  //
  //   window.location.href = encodeURI(`https://oauth.yandex.ru/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=${responseType}`)
  //
  //   }

}
