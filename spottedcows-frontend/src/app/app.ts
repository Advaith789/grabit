import { Component, signal } from '@angular/core';
// import { RouterOutlet } from '@angular/router';
import { UserPortal } from './user-portal/user-portal';
import { RestaurantSignup } from './restaurant-signup/restaurant-signup';
import { RouterOutlet, RouterLink } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, UserPortal, RestaurantSignup, RouterLink],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('spottedcows-frontend');
}
