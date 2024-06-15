import {Component, inject, OnInit} from '@angular/core';
import {LoginService} from "../../services/login.service";

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit {

  private loginService = inject(LoginService)

  ngOnInit() {
    this.loginService.loginUser()
  }

//   private oauth2GoogleService = inject(Oauth2GoogleService);
//   private router = inject(Router);
//   profile: any;
//
//   ngOnInit() {
//     this.showData();
//   }
//
//   showData() {
//     this.profile = this.oauth2GoogleService.getProfile();
//   }
//
//   logOut() {
// this.oauth2GoogleService.logout();
// this.router.navigate(['/login'])
// }
}

