import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { UserPortal } from './user-portal/user-portal';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, UserPortal],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('spottedcows-frontend');
}
