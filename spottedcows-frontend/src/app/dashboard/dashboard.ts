import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { environment } from '../../environments/environment';
import { Router } from '@angular/router';

interface DashboardItem {
  id: number;
  restaurant_name: string;
  food_item: string;
  cuisine: string;
  quantity: number;
}

@Component({
  selector: 'app-dashboard',
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})

export class Dashboard implements OnInit {
  inventoryData: DashboardItem[] = [];
  maxQuantity: number = 0;

  // Inject the Router and ChangeDetectorRef
  constructor(private http: HttpClient, private router: Router, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    // 1. Get the email from session storage
    const managerEmail = sessionStorage.getItem('restaurant_email');

    // 2. Security Check: If no email is found, redirect to login
    if (!managerEmail) {
      this.router.navigate(['/restaurant']);
      return; 
    }

    // 3. Fetch data using the dynamic email
    this.http.post<DashboardItem[]>(`${environment.apiUrl}/dashboard`, { 
      restaurant_email: managerEmail 
    }).subscribe({
      next: (data) => {
        this.inventoryData = data;
        
        if (data.length > 0) {
          this.maxQuantity = Math.max(...data.map(item => item.quantity));
        }
        this.cdr.detectChanges();
      },
      error: (err) => console.error('Failed to load dashboard data', err)
    });
  }

  getBarWidth(quantity: number): string {
    if (this.maxQuantity === 0) return '0%';
    const percentage = (quantity / this.maxQuantity) * 100;
    return `${percentage}%`;
  }
}
