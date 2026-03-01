import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { environment } from '../../environments/environment';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-restaurant-signup',
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './restaurant-signup.html',
  styleUrl: './restaurant-signup.css',
})
export class RestaurantSignup implements OnInit {
  step = 1; // 1: Email Check, 2: Prompt/Echo, 3: New Signup
  email = '';
  name = '';
  promptText = '';
  feedbackMessage = '';
  
  registeredEmails: string[] = [];

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    // Load existing restaurants to check against email input
    this.http.get<any[]>(`${environment.apiUrl}/restaurants`).subscribe({
      next: (res) => {
        // Extract just the emails for quick lookup
        this.registeredEmails = res.map(r => r.restaurant_email);
      },
      error: (err) => console.error('Failed to load restaurant list', err)
    });
  }

  checkRestaurantEmail() {
    window.sessionStorage.setItem('restaurant_email', this.email); // Store email for later use
    if (!this.email) return;

    if (this.registeredEmails.includes(this.email)) {
      this.step = 2; // Move to Prompt/Echo step
    } else {
      this.step = 3; // Move to Signup step
    }
    this.cdr.detectChanges();
  }

  // Step 2 logic: Echo/Prompt
  sendPrompt() {
    this.http.post(`${environment.apiUrl}/restaurant/prompt`, {
      restaurant_email: this.email,
      text: this.promptText
    }).subscribe({
      next: (res: any) => {
        this.feedbackMessage = `${res.echo || 'Yay! Your subsribers will be notified.'}`;
        this.cdr.detectChanges();
      },
      error: () => {
        this.feedbackMessage = 'Error sending prompt.';
        this.cdr.detectChanges();
      }
    });
  }

  // Step 3 logic: New Signup
  signUpRestaurant() {
    this.http.post(`${environment.apiUrl}/restaurants/signup`, {
      restaurant_name: this.name,
      restaurant_email: this.email
    }).subscribe({
      next: (res: any) => {
        this.feedbackMessage = res.message;
        if (res.message === 'Restaurant created') {
          this.step = 2; // Move to prompt area after successful signup
        }
        this.cdr.detectChanges();
      },
      error: () => {
        this.feedbackMessage = 'Signup failed.';
        this.cdr.detectChanges();
      }
    });
  }
}