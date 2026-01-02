import { Component, Output, EventEmitter } from "@angular/core";
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
import { MatProgressBarModule } from "@angular/material/progress-bar";
import { MatIconModule } from "@angular/material/icon";
import { MatSnackBar, MatSnackBarModule } from "@angular/material/snack-bar";
import { ApiService } from "../../core/services/api.service";
import { BacktestResults, JobStatus } from "../../core/models/models";

@Component({
  selector: "app-backtest-panel",
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatProgressBarModule,
    MatIconModule,
    MatSnackBarModule,
  ],
  template: `
    <div class="backtest-container">
      <!-- Configuration Form -->
      <mat-card class="config-card">
        <mat-card-header>
          <mat-icon mat-card-avatar>settings</mat-icon>
          <mat-card-title>Backtest Configuration</mat-card-title>
          <mat-card-subtitle>Configure backtest parameters</mat-card-subtitle>
        </mat-card-header>
        <mat-card-content>
          <form [formGroup]="backtestForm">
            <div class="form-grid">
              <mat-form-field>
                <mat-label>Period (Days)</mat-label>
                <input matInput type="number" formControlName="period_days" />
                <mat-hint>Number of days to backtest</mat-hint>
              </mat-form-field>

              <mat-form-field>
                <mat-label>Initial Capital (Optional)</mat-label>
                <input
                  matInput
                  type="number"
                  formControlName="initial_capital"
                />
                <mat-hint>Starting capital for calculations</mat-hint>
              </mat-form-field>
            </div>
          </form>
        </mat-card-content>
      </mat-card>

      <!-- Run Backtest Button -->
      <mat-card class="action-card">
        <mat-card-content>
          <div class="action-content">
            <div class="action-info">
              <mat-icon class="large-icon">assessment</mat-icon>
              <div>
                <h2>Run Backtest</h2>
                <p>Test your strategy on historical data</p>
              </div>
            </div>

            <button
              mat-raised-button
              color="primary"
              (click)="startBacktest()"
              [disabled]="isRunning || backtestForm.invalid"
              class="backtest-button"
            >
              <mat-icon>{{ results ? "refresh" : "play_arrow" }}</mat-icon>
              {{
                isRunning
                  ? "Running..."
                  : results
                  ? "Restart Backtest"
                  : "Start Backtest"
              }}
            </button>
          </div>
        </mat-card-content>
      </mat-card>

      <!-- Progress -->
      <mat-card class="progress-card" *ngIf="isRunning">
        <mat-card-header>
          <mat-icon mat-card-avatar class="spinning">sync</mat-icon>
          <mat-card-title>Backtest in Progress</mat-card-title>
          <mat-card-subtitle>{{ backtestStatus }}</mat-card-subtitle>
        </mat-card-header>
        <mat-card-content>
          <mat-progress-bar mode="determinate" [value]="backtestProgress">
          </mat-progress-bar>
          <p class="progress-text">{{ backtestProgress }}% Complete</p>
        </mat-card-content>
      </mat-card>

      <!-- Quick Results -->
      <mat-card class="quick-results-card" *ngIf="results">
        <mat-card-header>
          <mat-icon mat-card-avatar class="success-icon">check_circle</mat-icon>
          <mat-card-title>Backtest Complete!</mat-card-title>
        </mat-card-header>
        <mat-card-content>
          <div class="completion-message">
            <p>Results are displayed below.</p>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [
    `
      .backtest-container {
        max-width: 1200px;
        margin: 0 auto;
      }

      .config-card,
      .action-card,
      .progress-card,
      .quick-results-card {
        margin-bottom: 24px;
      }

      .form-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
      }

      .action-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 0;
      }

      .action-info {
        display: flex;
        align-items: center;
        gap: 16px;
      }

      .large-icon {
        font-size: 48px;
        width: 48px;
        height: 48px;
        color: #3f51b5;
      }

      .backtest-button {
        padding: 0 32px;
        height: 48px;
        font-size: 1.1rem;
      }

      .spinning {
        animation: spin 2s linear infinite;
      }

      @keyframes spin {
        0% {
          transform: rotate(0deg);
        }
        100% {
          transform: rotate(360deg);
        }
      }

      .progress-text {
        text-align: center;
        font-size: 1.1rem;
        font-weight: 500;
        color: #3f51b5;
        margin-top: 8px;
      }

      .success-icon {
        color: #4caf50 !important;
      }

      .completion-message {
        text-align: center;
        padding: 16px;
        color: var(--text-secondary);
        font-size: 1.1rem;
      }
    `,
  ],
})
export class BacktestPanelComponent {
  @Output() backtestComplete = new EventEmitter<BacktestResults>();

  backtestForm: FormGroup;
  isRunning = false;
  backtestProgress = 0;
  backtestStatus = "";
  results: BacktestResults | null = null;

  constructor(
    private fb: FormBuilder,
    private apiService: ApiService,
    private snackBar: MatSnackBar
  ) {
    this.backtestForm = this.fb.group({
      period_days: [350, [Validators.required, Validators.min(1)]],
      initial_capital: [10000],
    });
  }

  startBacktest() {
    if (this.backtestForm.invalid) return;

    this.isRunning = true;
    this.backtestProgress = 0;
    this.backtestStatus = "Starting backtest...";
    this.results = null;

    const params = this.backtestForm.value;

    this.apiService.startBacktest(params).subscribe({
      next: (response) => {
        this.pollBacktestStatus(response.job_id);
      },
      error: (error) => {
        this.handleError(error);
      },
    });
  }

  private pollBacktestStatus(jobId: string) {
    this.apiService.pollBacktestStatus(jobId).subscribe({
      next: (status: JobStatus) => {
        this.backtestProgress = status.progress;
        this.backtestStatus = status.message;

        if (status.status === "completed") {
          this.loadBacktestResults(jobId);
        } else if (status.status === "failed") {
          this.handleError(new Error(status.message));
        }
      },
      error: (error) => {
        this.handleError(error);
      },
    });
  }

  private loadBacktestResults(jobId: string) {
    this.apiService.getBacktestResults(jobId).subscribe({
      next: (results) => {
        this.results = results;
        this.isRunning = false;
        this.backtestComplete.emit(results);
      },
      error: (error) => {
        this.handleError(error);
      },
    });
  }

  private handleError(error: any) {
    this.isRunning = false;
    const errorMsg = error.message || "Backtest failed";
    this.snackBar.open(errorMsg, "Close", {
      duration: 5000,
      panelClass: ["error-snackbar"],
    });
  }
}
