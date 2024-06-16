import { Routes } from '@angular/router';
import {LoginComponent} from "./components/login/login.component";
import {DashboardComponent} from "./components/dashboard/dashboard.component";
import {Dashboard2Component} from "./components/dashboard2/dashboard2.component";
import {ExerciseComponent} from "./components/exercise/exercise.component";

export const routes: Routes = [
  {path: '', redirectTo: '/login', pathMatch: 'full'},
  {path: 'login', component: LoginComponent},
  {path: 'googleOauth2callback', component: DashboardComponent},
  {path: 'yandexOauth2callback', component: Dashboard2Component},
  {path: 'exercise', component: ExerciseComponent},
];
