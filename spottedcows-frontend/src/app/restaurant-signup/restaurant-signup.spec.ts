import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RestaurantSignup } from './restaurant-signup';

describe('RestaurantSignup', () => {
  let component: RestaurantSignup;
  let fixture: ComponentFixture<RestaurantSignup>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RestaurantSignup],
    }).compileComponents();

    fixture = TestBed.createComponent(RestaurantSignup);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
