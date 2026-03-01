import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common'; 
import { FormsModule } from '@angular/forms';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-user-portal',
  imports: [CommonModule, FormsModule],
  templateUrl: './user-portal.html',
  styleUrl: './user-portal.css',
})
export class UserPortal implements OnInit {
  step = 1; 
  email = '';
  name = '';
  
  allRestaurants: any[] = [];
  userRestaurants: string[] = [];

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    // 2. Swapped hardcoded URL for environment variable
    this.http.get(`${environment.apiUrl}/restaurants`).subscribe({
      next: (res: any) => this.allRestaurants = res,
      error: (err) => console.error('Could not load restaurants', err)
    });
  }

  checkEmail() {
    if (!this.email) return;

    // 3. Swapped hardcoded URL for environment variable
    this.http.post(`${environment.apiUrl}/users/details`, { user_email: this.email }).subscribe({
      next: (res: any) => {
        this.name = res.user_name;
        this.userRestaurants = res.preferences || [];
        this.step = 2; 
        this.cdr.detectChanges();
        console.log('User details loaded', this.allRestaurants);
      },
      error: (err) => {
        if (err.status === 404) this.step = 3; 
        this.cdr.detectChanges();
      }
    });
  }

  toggleRestaurant(restName: string, event: any) {
    if (event.target.checked) {
      this.userRestaurants.push(restName);
    } else {
      this.userRestaurants = this.userRestaurants.filter(r => r !== restName);
    }
  }

  signUp() {
    this.http.post(`${environment.apiUrl}/users/signup`, {
      user_name: this.name,             // Changed from 'name'
      user_email: this.email,           // Changed from 'email'
      preferences: this.userRestaurants // Changed from 'restaurants'
    }).subscribe({
      next: () => {
        this.step = 2; 
        this.cdr.detectChanges(); // Ensures the screen updates
      },
      error: () => alert('Sign up failed')
    });
  }
}