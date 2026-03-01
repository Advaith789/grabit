import { Routes } from '@angular/router';
import { UserPortal } from './user-portal/user-portal';
import { RestaurantSignup } from './restaurant-signup/restaurant-signup';

export const routes: Routes = [
    { path: '', component: UserPortal },              // Default path for users
  { path: 'restaurant', component: RestaurantSignup }, // Path for restaurants
  { path: '**', redirectTo: '' }
];
