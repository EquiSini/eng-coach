import {Component, inject, OnInit} from '@angular/core';
import {LoginService} from "../../services/login.service";

@Component({
  selector: 'app-dashboard2',
  standalone: true,
  imports: [],
  templateUrl: './dashboard2.component.html',
  styleUrl: './dashboard2.component.scss'
})
export class Dashboard2Component implements OnInit {

  private loginService = inject(LoginService)

  ngOnInit() {
    this.loginService.loginUser()
  }

}
