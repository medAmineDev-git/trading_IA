import { Component, Output, EventEmitter, Input } from "@angular/core";
import { CommonModule } from "@angular/common";
import {
  FormBuilder,
  FormGroup,
  FormControl,
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
import { AuthService } from "../../core/services/auth.service";
import {
  BacktestResults,
  JobStatus,
  TrainingParams,
  Strategy,
} from "../../core/models/models";

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
                <mat-error
                  *ngIf="backtestForm.get('period_days')?.hasError('min')"
                >
                  Must be at least 1 day
                </mat-error>
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

      <!-- Quick Results & Save -->
      <mat-card class="quick-results-card" *ngIf="results">
        <mat-card-header>
          <mat-icon mat-card-avatar class="success-icon">check_circle</mat-icon>
          <mat-card-title>Backtest Complete!</mat-card-title>
        </mat-card-header>
        <mat-card-content>
          <div class="completion-message">
            <p>Results are displayed below.</p>
          </div>

          <!-- Save Strategy Form -->
          <div class="save-strategy-section glass-panel">
            <h3>Save Strategy</h3>
            <div class="save-form">
              <mat-form-field appearance="outline" class="name-input">
                <mat-label>Strategy Name</mat-label>
                <input
                  matInput
                  [formControl]="strategyNameControl"
                  placeholder="e.g. Aggressive Scalper v1"
                />
              </mat-form-field>
              <button
                mat-raised-button
                color="accent"
                (click)="saveStrategy()"
                [disabled]="isSaving || strategyNameControl.invalid"
              >
                <mat-icon>save</mat-icon>
                {{ isSaving ? "Saving..." : "Save Strategy" }}
              </button>
            </div>
            <p class="save-hint" *ngIf="!isAuthenticated">
              <mat-icon inline>info</mat-icon> You must be logged in to save
              strategies.
            </p>
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

      .save-strategy-section {
        margin-top: 24px;
        padding: 16px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
      }

      .save-strategy-section h3 {
        margin-top: 0;
        margin-bottom: 16px;
        font-size: 1.1rem;
        color: var(--text-primary);
      }

      .save-form {
        display: flex;
        gap: 16px;
        align-items: flex-start;
      }

      .name-input {
        flex: 1;
      }

      .save-hint {
        margin-top: 8px;
        font-size: 0.9rem;
        color: var(--text-secondary);
        display: flex;
        align-items: center;
        gap: 4px;
      }
    `,
  ],
})
export class BacktestPanelComponent {
  @Input() params: TrainingParams | null = null;
  @Output() backtestComplete = new EventEmitter<BacktestResults>();
  @Output() strategySaved = new EventEmitter<Strategy>();

  backtestForm: FormGroup;
  strategyNameControl: FormControl;
  isRunning = false;
  isSaving = false;
  backtestProgress = 0;
  backtestStatus = "";
  results: BacktestResults | null = null;
  isAuthenticated = false;

  constructor(
    private fb: FormBuilder,
    private apiService: ApiService,
    private authService: AuthService,
    private snackBar: MatSnackBar
  ) {
    this.backtestForm = this.fb.group({
      period_days: [350, [Validators.required, Validators.min(1)]],
      initial_capital: [10000],
    });

    this.strategyNameControl = new FormControl("", [Validators.required]);

    this.authService.user$.subscribe((user) => {
      this.isAuthenticated = !!user;
      if (!this.isAuthenticated) {
        this.strategyNameControl.disable();
      } else {
        this.strategyNameControl.enable();
      }
    });
  }

  startBacktest() {
    if (this.backtestForm.invalid) return;

    this.isRunning = true;
    this.backtestProgress = 0;
    this.backtestStatus = "Starting backtest...";
    this.results = null;

    // Merge period_days with general training/model params
    const backtestParams = {
      ...this.params,
      ...this.backtestForm.getRawValue(),
    };

    this.apiService.startBacktest(backtestParams).subscribe({
      next: (response) => {
        this.pollBacktestStatus(response.job_id);
      },
      error: (error) => {
        this.handleError(error);
      },
    });
  }

  saveStrategy() {
    if (this.strategyNameControl.invalid || !this.isAuthenticated) return;

    const name = this.strategyNameControl.value;
    this.isSaving = true;

    this.apiService.savePersonalStrategy(name).subscribe({
      next: (response) => {
        this.isSaving = false;
        this.snackBar.open("Strategy saved successfully!", "Close", {
          duration: 3000,
          panelClass: ["success-snackbar"],
        });
        this.strategyNameControl.reset();
        this.strategySaved.emit(response.strategy);
      },
      error: (error) => {
        this.isSaving = false;
        this.snackBar.open(error.message, "Close", {
          duration: 5000,
          panelClass: ["error-snackbar"],
        });
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
    this.isSaving = false;
    const errorMsg = error.message || "Backtest failed";
    this.snackBar.open(errorMsg, "Close", {
      duration: 5000,
      panelClass: ["error-snackbar"],
    });
  }
}
