import { Component, OnInit } from "@angular/core";
import { CommonModule } from "@angular/common";
import { MatTabsModule } from "@angular/material/tabs";
import { MatCardModule } from "@angular/material/card";

import { MatDividerModule } from "@angular/material/divider";

import { MatButtonModule } from "@angular/material/button";
import { MatIconModule } from "@angular/material/icon";
import { MatSnackBar, MatSnackBarModule } from "@angular/material/snack-bar";
import { ParametersFormComponent } from "../parameters/parameters-form.component";
import { TrainingPanelComponent } from "../training/training-panel.component";
import { BacktestPanelComponent } from "../backtesting/backtest-panel.component";
import { ResultsDashboardComponent } from "../results/results-dashboard.component";
import { TopStrategiesComponent } from "../top-strategies/top-strategies.component";
import { ApiService } from "../../core/services/api.service";
import { TrainingParams, BacktestResults } from "../../core/models/models";

@Component({
  selector: "app-dashboard",
  standalone: true,
  imports: [
    CommonModule,
    MatTabsModule,
    MatCardModule,

    MatDividerModule,

    MatButtonModule,
    MatIconModule,
    MatSnackBarModule,
    ParametersFormComponent,
    TrainingPanelComponent,
    BacktestPanelComponent,
    ResultsDashboardComponent,
    TopStrategiesComponent,
  ],
  template: `
    <div class="dashboard-container">
      <!-- Hero Section -->
      <section class="hero-section">
        <h1 class="hero-title">
          Master Your Trading with <br />
          <span class="text-gradient">FundedLab</span>
        </h1>
        <p class="hero-subtitle">
          Configure, Train, Backtest, and Analyze your strategies with our
          advanced ML engine.
        </p>

        <div class="stats-row">
          <div class="stat-badge">
            <span class="label">Status</span>
            <span class="value text-gradient">Active</span>
          </div>
          <div class="stat-badge">
            <span class="label">Model</span>
            <span class="value">{{
              getModelDisplayName(trainingParams?.model?.model_type)
            }}</span>
          </div>

          <button
            mat-flat-button
            color="accent"
            (click)="openParams()"
            *ngIf="!showParamsCard"
          >
            <mat-icon>tune</mat-icon>
            Configure Training Parameters
          </button>
        </div>

        <!-- Configuration Card -->
        <div class="config-card glass-panel" *ngIf="showParamsCard">
          <div class="config-header">
            <h2>Training Parameters</h2>
            <button mat-icon-button (click)="closeParams(false)">
              <mat-icon>close</mat-icon>
            </button>
          </div>

          <app-parameters-form
            [initialParams]="trainingParams"
            (paramsChange)="onParamsChange($event)"
          >
          </app-parameters-form>

          <div class="card-multi-actions">
            <button mat-button (click)="closeParams(false)">Cancel</button>
            <button
              mat-raised-button
              color="primary"
              (click)="closeParams(true)"
            >
              <mat-icon>check</mat-icon>
              Validate
            </button>
          </div>
        </div>
      </section>

      <!-- Main Content Tabs -->
      <div class="glass-panel main-content-panel">
        <mat-tab-group
          [(selectedIndex)]="selectedTabIndex"
          (selectedIndexChange)="onTabChange($event)"
          animationDuration="0ms"
          mat-stretch-tabs="false"
          mat-align-tabs="center"
          class="custom-tabs"
        >
          <!-- Training Tab -->
          <mat-tab label="Training">
            <div class="tab-content">
              <app-training-panel
                [params]="trainingParams"
                (trainingComplete)="onTrainingComplete()"
              >
              </app-training-panel>

              <div class="manual-nav">
                <button
                  mat-raised-button
                  color="primary"
                  class="action-button"
                  [disabled]="!isModelTrained"
                  (click)="goToBacktest()"
                >
                  <mat-icon>assessment</mat-icon>
                  Backtest Trained Model
                </button>
              </div>
            </div>
          </mat-tab>

          <!-- Backtest Tab -->
          <mat-tab label="Backtest">
            <div class="tab-content">
              <app-backtest-panel
                (backtestComplete)="onBacktestComplete($event)"
              >
              </app-backtest-panel>

              <!-- Results Display Section -->
              <div class="results-container" *ngIf="backtestResults">
                <mat-divider style="margin: 24px 0"></mat-divider>
                <h3 class="results-title">Backtest Results</h3>
                <app-results-dashboard
                  [results]="backtestResults"
                ></app-results-dashboard>
              </div>
            </div>
          </mat-tab>

          <!-- Top Strategies Tab -->
          <mat-tab>
            <ng-template mat-tab-label>
              <mat-icon style="margin-right: 8px">military_tech</mat-icon>
              Top Strategies
            </ng-template>
            <div class="tab-content">
              <app-top-strategies></app-top-strategies>
            </div>
          </mat-tab>
        </mat-tab-group>
      </div>
    </div>
  `,
  styles: [
    `
      .dashboard-container {
        padding: 40px 24px;
        max-width: 1200px;
        margin: 0 auto;
      }

      /* Hero Section */
      .hero-section {
        text-align: center;
        margin-bottom: 60px;
        position: relative;
        z-index: 1;

        &::before {
          content: "";
          position: absolute;
          top: -50%; // fixed to avoid syntax error
          left: 50%;
          transform: translateX(-50%);
          width: 600px;
          height: 600px;
          background: radial-gradient(
            circle,
            rgba(146, 98, 249, 0.15) 0%,
            rgba(0, 0, 0, 0) 70%
          );
          z-index: -1;
          pointer-events: none;
        }
      }

      .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        line-height: 1.2;
        margin-bottom: 16px;
        letter-spacing: -1px;
      }

      .hero-subtitle {
        font-size: 1.1rem;
        color: var(--text-secondary);
        max-width: 600px;
        margin: 0 auto 32px auto;
      }

      .stats-row {
        display: flex;
        justify-content: center;
        gap: 16px;
      }

      .stat-badge {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 8px 16px;
        border-radius: 50px;
        font-size: 0.9rem;

        .label {
          color: var(--text-secondary);
        }

        .value {
          font-weight: 600;
          color: var(--text-primary);
        }
      }

      /* Main Content Panel */
      .main-content-panel {
        padding: 24px;
        min-height: 600px;
        background: rgba(
          30,
          30,
          30,
          0.4
        ); /* Slightly different from standard glass for contrast */
      }

      /* Custom Tabs Styling Overrides */
      ::ng-deep .custom-tabs {
        .mat-mdc-tab-labels {
          background-color: transparent !important;
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .mat-mdc-tab-link-container {
          border-bottom-color: rgba(255, 255, 255, 0.1);
        }

        .mat-mdc-tab {
          font-family: var(--font-heading);
          letter-spacing: 0.5px;
          color: var(--text-secondary);
          padding: 0 24px;
        }

        .mdc-tab--active .mdc-tab__text-label {
          color: var(--text-primary) !important;
        }

        .mat-mdc-tab-group.mat-primary
          .mat-mdc-tab:not(.mat-mdc-tab-disabled).mdc-tab--active
          .mdc-tab__text-label,
        .mat-mdc-tab-group.mat-primary
          .mat-mdc-tab-link:not(.mat-mdc-tab-disabled).mdc-tab--active
          .mdc-tab__text-label {
          color: var(--text-primary);
        }

        .mdc-tab-indicator__content--underline {
          border-color: var(--text-accent) !important;
        }
      }

      .config-actions {
        display: flex;
        justify-content: center;
        margin-bottom: 24px;
      }

      .config-card {
        margin-bottom: 24px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        animation: slideDown 0.3s ease-out;
      }

      .config-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;

        h2 {
          margin: 0;
          font-size: 1.5rem;
          color: var(--text-primary);
        }
      }

      .card-multi-actions {
        display: flex;
        justify-content: flex-end;
        gap: 16px;
        margin-top: 24px;
        padding-top: 16px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
      }

      @keyframes slideDown {
        from {
          opacity: 0;
          transform: translateY(-20px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      .manual-nav {
        display: flex;
        justify-content: center;
        padding: 24px 0;
        margin-top: 24px;
      }

      .action-button {
        padding: 0 32px;
        height: 48px;
        font-size: 1.1rem;
      }

      .action-button mat-icon {
        margin-right: 8px;
      }

      .results-title {
        text-align: center;
        margin: 24px 0;
        font-size: 1.5rem;
        color: var(--text-primary);
      }
    `,
  ],
})
export class DashboardComponent implements OnInit {
  selectedTabIndex = 0;
  trainingParams: TrainingParams | null = null;
  lastSavedParams: TrainingParams | null = null;
  backtestResults: BacktestResults | null = null;

  showParamsCard = false;
  isModelTrained = false;

  constructor(private apiService: ApiService, private snackBar: MatSnackBar) {}

  ngOnInit() {
    // Load default configuration
    this.apiService.getConfig().subscribe({
      next: (config) => {
        this.trainingParams = {
          indicators: config.indicators,
          risk: config.risk,
          model: config.model,
          data: {
            csv_path: config.data.mt5_csv_path,
            training_period: config.data.training_period,
          },
        };
      },
      error: (error) => {
        this.snackBar.open(
          "Failed to load configuration. Is the API server running?",
          "Close",
          {
            duration: 5000,
            panelClass: ["error-snackbar"],
          }
        );
      },
    });
  }

  onParamsChange(params: TrainingParams) {
    // Live update for validation state tracking, but effectively 'temporary' until validated
    this.trainingParams = params;
  }

  openParams() {
    // Snapshot current params for cancellation
    if (this.trainingParams) {
      this.lastSavedParams = JSON.parse(JSON.stringify(this.trainingParams));
    }
    this.showParamsCard = true;
  }

  closeParams(validate: boolean) {
    if (!validate && this.lastSavedParams) {
      // Revert to snapshot
      this.trainingParams = this.lastSavedParams;
    }
    // If validate is true, we just keep the current this.trainingParams which has been updating via onParamsChange
    this.showParamsCard = false;
    this.lastSavedParams = null;
  }

  onTrainingComplete() {
    this.snackBar.open("Training completed successfully!", "Close", {
      duration: 3000,
      panelClass: ["success-snackbar"],
    });

    // Mark as trained, enable button, BUT DO NOT auto-switch
    this.isModelTrained = true;
    // this.selectedTabIndex = 2; // Auto-switch removed
  }

  onBacktestComplete(results: BacktestResults) {
    this.backtestResults = results;
    this.snackBar.open("Backtest completed successfully!", "Close", {
      duration: 3000,
      panelClass: ["success-snackbar"],
    });
    // No auto-switch needed as results appear in current tab
  }

  goToBacktest() {
    this.selectedTabIndex = 1; // Index 1 is the Backtest tab (Training is 0, Results is 2... wait, Training is 0, Backtest is 1, Results is 2 based on current layout? No, index check needed)
    // Actually, checking template:
    // Tab 0: Training (Parameters removed)
    // Tab 1: Backtest
    // Tab 2: Results
    this.selectedTabIndex = 1;
  }

  onTabChange(index: number) {
    // You can add logic here if needed when tabs change
  }

  getModelDisplayName(type: string | undefined): string {
    const map: { [key: string]: string } = {
      xgboost: "XGBoost",
      lightgbm: "LightGBM",
      rf: "Random Forest",
    };
    return map[type || ""] || "Not Configured";
  }
}
