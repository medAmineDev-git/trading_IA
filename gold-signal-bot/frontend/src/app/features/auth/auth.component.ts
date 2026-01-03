import { Component } from "@angular/core";
import { CommonModule } from "@angular/common";
import {
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from "@angular/forms";
import { MatCardModule } from "@angular/material/card";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatInputModule } from "@angular/material/input";
import { MatButtonModule } from "@angular/material/button";
import { MatIconModule } from "@angular/material/icon";
import { MatSnackBar } from "@angular/material/snack-bar";
import { AuthService } from "../../core/services/auth.service";

@Component({
  selector: "app-auth",
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
  ],
  template: `
    <div class="auth-container">
      <mat-card class="auth-card">
        <mat-card-header>
          <mat-icon mat-card-avatar color="primary">{{
            isLogin ? "login" : "person_add"
          }}</mat-icon>
          <mat-card-title>{{
            isLogin ? "Welcome Back" : "Create Account"
          }}</mat-card-title>
          <mat-card-subtitle>{{
            isLogin
              ? "Login to manage your strategies"
              : "Register to save and publish strategies"
          }}</mat-card-subtitle>
        </mat-card-header>
        <mat-card-content>
          <form [formGroup]="authForm" (ngSubmit)="onSubmit()">
            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Email</mat-label>
              <input
                matInput
                type="email"
                formControlName="email"
                placeholder="Ex. pat@example.com"
              />
              <mat-error *ngIf="authForm.get('email')?.hasError('required')">
                Email is required
              </mat-error>
              <mat-error *ngIf="authForm.get('email')?.hasError('email')">
                Please enter a valid email
              </mat-error>
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Password</mat-label>
              <input
                matInput
                [type]="hidePassword ? 'password' : 'text'"
                formControlName="password"
              />
              <button
                mat-icon-button
                matSuffix
                (click)="hidePassword = !hidePassword"
                [attr.aria-label]="'Hide password'"
                [attr.aria-pressed]="hidePassword"
                type="button"
              >
                <mat-icon>{{
                  hidePassword ? "visibility_off" : "visibility"
                }}</mat-icon>
              </button>
              <mat-error *ngIf="authForm.get('password')?.hasError('required')">
                Password is required
              </mat-error>
            </mat-form-field>

            <button
              mat-raised-button
              color="primary"
              type="submit"
              class="full-width submit-btn"
              [disabled]="loading || authForm.invalid"
            >
              {{ loading ? "Processing..." : isLogin ? "Login" : "Register" }}
            </button>
          </form>

          <div class="toggle-view">
            <p>
              {{
                isLogin ? "Don't have an account?" : "Already have an account?"
              }}
              <a href="javascript:void(0)" (click)="toggleView()">
                {{ isLogin ? "Register" : "Login" }}
              </a>
            </p>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [
    `
      .auth-container {
        display: flex;
        justify-content: center;
        padding: 40px 20px;
      }

      .auth-card {
        max-width: 400px;
        width: 100%;
      }

      .full-width {
        width: 100%;
        margin-bottom: 8px;
      }

      .submit-btn {
        margin-top: 16px;
        height: 48px;
        font-size: 1.1rem;
      }

      .toggle-view {
        margin-top: 24px;
        text-align: center;
        color: var(--text-secondary);
      }

      .toggle-view a {
        color: #3f51b5;
        text-decoration: none;
        font-weight: 500;
        margin-left: 4px;
      }

      .toggle-view a:hover {
        text-decoration: underline;
      }

      mat-card-header {
        margin-bottom: 24px;
      }
    `,
  ],
})
export class AuthComponent {
  isLogin = true;
  hidePassword = true;
  loading = false;
  authForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private snackBar: MatSnackBar
  ) {
    this.authForm = this.fb.group({
      email: ["", [Validators.required, Validators.email]],
      password: ["", [Validators.required, Validators.minLength(6)]],
    });
  }

  toggleView() {
    this.isLogin = !this.isLogin;
    this.authForm.reset();
  }

  onSubmit() {
    if (this.authForm.invalid) return;

    this.loading = true;
    const data = this.authForm.value;
    const action$ = this.isLogin
      ? this.authService.login(data)
      : this.authService.register(data);

    action$.subscribe({
      next: (response) => {
        this.loading = false;
        if (response.user) {
          this.snackBar.open(
            `Successfully ${this.isLogin ? "logged in" : "registered"}!`,
            "Close",
            {
              duration: 3000,
              panelClass: ["success-snackbar"],
            }
          );
        } else {
          this.snackBar.open(response.message || "Operation failed", "Close", {
            duration: 3000,
          });
        }
      },
      error: (error) => {
        this.loading = false;
        this.snackBar.open(error.message || "An error occurred", "Close", {
          duration: 3000,
          panelClass: ["error-snackbar"],
        });
      },
    });
  }
}
