import {inject, Injectable} from '@angular/core';
import {LoginCodeType} from "../interfaces/login-code-type";
import {HttpClient} from "@angular/common/http";
import {catchError, Observable, tap} from "rxjs";
// import {error} from "@angular/compiler-cli/src/transformers/util";!!!!!!
import {environment} from "../../environments/environment";


@Injectable({
  providedIn: 'root'
})
export class LoginService {

  private httpClient: HttpClient = inject(HttpClient);

  constructor() { }

  showLogin: boolean = true
  loginWithGoogle() {

    const clientId: string = environment.GOOGLE_CLIENT_ID;
    const redirectUri: string = 'http://localhost/googleOauth2callback';
    const responseType: string = 'code';
    const scope: string = 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile';
    const includeGrantedScopes: string = 'true';
    const state: string = 'pass-through value';

    window.location.href = encodeURI(`https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=${responseType}&scope=${scope}&include_granted_scopes=${includeGrantedScopes}&state=${state}`)
  }

  loginWithYandex() {

    const clientId: string = environment.YANDEX_CLIENT_ID;
    const redirectUri : string = 'http://localhost/yandexOauth2callback';
    const responseType: string = 'code'

    window.location.href = encodeURI(`https://oauth.yandex.ru/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=${responseType}`)

  }

  loginUser() {

    const url = new URL (`${window.location}`)
    const searchParams = url.searchParams;
    const code = searchParams.get("code")
    let type: string
    if (url.pathname === "/yandexOauth2callback") {
      type = "yandex"
    } else {type = "google"}

    if (code&&type) {
      const info: LoginCodeType = {
        code: code,
        oauth_service: type
      }
      // const infoJson = JSON.stringify(info)
      console.log(info)
      this.httpClient.post('http://localhost/api/login', info)
        .subscribe({
          next: value => {
           console.log(value)

            // this.router.navigate(["all-meetups"])
          },
          error: err => {
            console.error(err);
            // this.message = "Something went wrong. Please try again"
          },
          // complete: () => console.log('Complete and unsubscribe')
        });

    }

  }
}
