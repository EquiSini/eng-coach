import {inject, Injectable} from '@angular/core';
import {LoginCodeType} from "../interfaces/login-code-type";
import {HttpClient} from "@angular/common/http";
import {BehaviorSubject, catchError, Observable, tap} from "rxjs";
// import {error} from "@angular/compiler-cli/src/transformers/util";!!!!!!
import {environment} from "../../environments/environment";
import {UserData} from "../interfaces/user-data";
import {Router} from "@angular/router";


@Injectable({
  providedIn: 'root'
})
export class LoginService {

  private httpClient: HttpClient = inject(HttpClient);
  private router = inject(Router)
  private _user$: BehaviorSubject<UserData | null> = new BehaviorSubject<UserData | null>(null);
  private _isLoggedIn$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);

  public get user$(): Observable<UserData | null> {
    return this._user$.asObservable()
  }

  public get isLoggedIn$(): Observable<boolean> {
    return this._isLoggedIn$.asObservable()
  }

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
    const redirectUri: string = 'http://localhost/yandexOauth2callback';
    const responseType: string = 'code'

    window.location.href = encodeURI(`https://oauth.yandex.ru/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=${responseType}`)

  }

  loginUser() {

    const url = new URL(`${window.location}`)
    const searchParams = url.searchParams;
    const code = searchParams.get("code")
    let type: string
    if (url.pathname === "/yandexOauth2callback") {
      type = "yandex"
    } else {
      type = "google"
    }

    if (code && type) {
      const info: LoginCodeType = {
        code: code,
        oauth_service: type
      }
      // const infoJson = JSON.stringify(info)
      console.log(info)
      this.httpClient.post<UserData | null>('http://localhost/api/login', info)
        .subscribe({
          next: value => {
            console.log(value)
            this._user$.next(value)
            this._isLoggedIn$.next(true)
            this.router.navigate(["exercise"])
          },
          error: err => {
            console.error(err);
            // this.message = "Something went wrong. Please try again"
          },
          // complete: () => console.log('Complete and unsubscribe')
        });
    }
  }

  logout() {
    this._user$.next(null)
    this._isLoggedIn$.next(false)
  }
}
