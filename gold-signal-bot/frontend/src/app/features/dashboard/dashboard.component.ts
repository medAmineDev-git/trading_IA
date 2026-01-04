import { Component, OnInit } from "@angular/core";
import { CommonModule } from "@angular/common";
import { MatTabsModule } from "@angular/material/tabs";
import { MatCardModule } from "@angular/material/card";

import { MatDividerModule } from "@angular/material/divider";

import { MatButtonModule } from "@angular/material/button";
import { MatIconModule } from "@angular/material/icon";
import { MatSnackBar, MatSnackBarModule } from "@angular/material/snack-bar";
import { MatSlideToggleModule } from "@angular/material/slide-toggle";
import { ParametersFormComponent } from "../parameters/parameters-form.component";
import { TrainingPanelComponent } from "../training/training-panel.component";
import { BacktestPanelComponent } from "../backtesting/backtest-panel.component";
import { ResultsDashboardComponent } from "../results/results-dashboard.component";
import { TopStrategiesComponent } from "../top-strategies/top-strategies.component";
import { ApiService } from "../../core/services/api.service";
import {
  TrainingParams,
  TrainingResults,
  JobStatus,
  BacktestResults,
  Strategy,
  User,
} from "../../core/models/models";
import { AuthComponent } from "../auth/auth.component";
import { MyStrategiesComponent } from "../my-strategies/my-strategies.component";
import { AuthService } from "../../core/services/auth.service";

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
    MatSlideToggleModule,
    ParametersFormComponent,
    TrainingPanelComponent,
    BacktestPanelComponent,
    ResultsDashboardComponent,
    TopStrategiesComponent,
    AuthComponent,
    MyStrategiesComponent,
  ],
  template: `
    <div class="dashboard-container">
      <!-- Detail View Area (Conditional) -->
      <div
        class="detail-view-container"
        *ngIf="selectedStrategy; else mainView"
      >
        <div class="detail-header glass-panel mb-16">
          <button mat-icon-button (click)="closeDetailView()">
            <mat-icon>arrow_back</mat-icon>
          </button>
          <div class="header-info">
            <h2 class="text-gradient">{{ selectedStrategy.name }}</h2>
            <p class="subtitle">Strategy Insights & Backtest Analysis</p>
          </div>
        </div>

        <div class="glass-panel detail-content">
          <div class="premium-locked-section" [class.locked]="isViewOnly">
            <div class="premium-badge-overlay" *ngIf="isViewOnly">
              <mat-icon>lock</mat-icon>
              <span>Premium Strategy Configuration</span>
              <mat-slide-toggle
                [disabled]="true"
                [checked]="true"
                color="accent"
              >
                Active
              </mat-slide-toggle>
            </div>
            <app-training-panel
              [params]="selectedStrategy.training.params"
              [showTrainButton]="false"
            >
            </app-training-panel>
          </div>

          <mat-divider style="margin: 40px 0"></mat-divider>

          <app-backtest-panel
            *ngIf="!isViewOnly"
            [params]="selectedStrategy.training.params"
            (backtestComplete)="onBacktestComplete($event)"
          >
          </app-backtest-panel>

          <!-- MT5 Subscription Section (Placeholder) -->
          <div
            class="mt5-subscription-section glass-panel mt-24"
            *ngIf="isViewOnly"
          >
            <div class="subscription-header">
              <mat-icon color="accent" class="large-icon"
                >account_balance_wallet</mat-icon
              >
              <div>
                <h3>Subscribe with MT5</h3>
                <p>
                  Connect your MetaTrader 5 account to follow this strategy
                  automatically.
                </p>
              </div>
            </div>

            <div class="subscription-content">
              <div class="feature-item">
                <mat-icon>check_circle</mat-icon>
                <span>Real-time signal execution</span>
              </div>
              <div class="feature-item">
                <mat-icon>check_circle</mat-icon>
                <span>Automated risk management</span>
              </div>
              <div class="feature-item">
                <mat-icon>check_circle</mat-icon>
                <span>Daily performance reports</span>
              </div>

              <button
                mat-raised-button
                color="accent"
                class="subscribe-btn"
                disabled
              >
                <mat-icon>bolt</mat-icon>
                Coming Soon - MT5 Integration
              </button>
            </div>
          </div>

          <div class="results-container" *ngIf="backtestResults">
            <mat-divider style="margin: 24px 0"></mat-divider>
            <h3 class="results-title">Backtest Results</h3>
            <app-results-dashboard
              [results]="backtestResults"
            ></app-results-dashboard>
          </div>
        </div>
      </div>

      <!-- Main Dashboard View -->
      <ng-template #mainView>
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
                selectedTabIndex === 1
                  ? "Multi-model"
                  : getModelDisplayName(trainingParams?.model?.model_type)
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
            <mat-tab label="Training Strategy">
              <div class="tab-content">
                <!-- Strategy Explanation & Quick Actions -->
                <div class="strategy-info-section mb-24">
                  <div class="info-content">
                    <div class="model-info-header">
                      <div class="model-badge">
                        <mat-icon>{{
                          trainingParams?.model?.model_type === "ensemble"
                            ? "hub"
                            : "psychology"
                        }}</mat-icon>
                        <span>{{
                          getModelDisplayName(trainingParams?.model?.model_type)
                        }}</span>
                      </div>
                      <h3>
                        {{
                          trainingParams?.model?.model_type === "ensemble"
                            ? "🚀 Elite Voting Ensemble"
                            : "Selected ML Strategy"
                        }}
                      </h3>
                    </div>

                    <p class="description">
                      {{
                        trainingParams?.model?.model_type === "ensemble"
                          ? "Combining XGBoost, LightGBM, and Random Forest for maximum signal reliability through consensus voting."
                          : trainingParams?.model?.model_type === "xgboost"
                          ? "Industry-standard gradient boosting optimized for gold market volatility and complex patterns."
                          : "Advanced machine learning model configured for high-precision trade entries."
                      }}
                    </p>

                    <div class="config-nudge-box glass-panel">
                      <div class="nudge-text">
                        <mat-icon color="accent">tips_and_updates</mat-icon>
                        <p>
                          We recommend you to change the parameters and models
                          if you want to optimize results.
                        </p>
                      </div>
                      <button
                        mat-flat-button
                        color="accent"
                        (click)="openParams()"
                        class="config-btn"
                      >
                        <mat-icon>tune</mat-icon>
                        Configure Parameters
                      </button>
                    </div>
                  </div>
                </div>

                <app-training-panel
                  [params]="trainingParams"
                  (trainingComplete)="onTrainingComplete()"
                >
                </app-training-panel>

                <!-- Backtest Display Section - Only shown after training -->
                <div
                  class="backtest-section"
                  *ngIf="isModelTrained || isEnsembleModelTrained"
                  style="margin-top: 40px;"
                >
                  <mat-divider style="margin-bottom: 40px;"></mat-divider>

                  <app-backtest-panel
                    [params]="trainingParams"
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
              </div>
            </mat-tab>

            <!-- Top Strategies Tab -->
            <mat-tab>
              <ng-template mat-tab-label>
                <mat-icon style="margin-right: 8px">military_tech</mat-icon>
                Top Strategies
              </ng-template>
              <div class="tab-content">
                <app-top-strategies
                  (backtestSelected)="onStrategyBacktest($event)"
                ></app-top-strategies>
              </div>
            </mat-tab>
            <!-- My Strategies Tab -->
            <mat-tab>
              <ng-template mat-tab-label>
                <mat-icon style="margin-right: 8px">person</mat-icon>
                My Strategies
              </ng-template>
              <div class="tab-content" style="min-height: 400px;">
                <app-my-strategies
                  *ngIf="user; else authView"
                ></app-my-strategies>
                <ng-template #authView>
                  <app-auth></app-auth>
                </ng-template>
              </div>
            </mat-tab>
          </mat-tab-group>
        </div>
      </ng-template>
    </div>
  `,
  styles: [
    `
      .dashboard-container {
        padding: 40px 24px;
        max-width: 1200px;
        margin: 0 auto;
      }

      .detail-header {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 16px 24px;
        border-radius: 16px;

        .header-info {
          h2 {
            margin: 0;
            font-size: 1.8rem;
          }
          .subtitle {
            margin: 0;
            color: var(--text-secondary);
            font-size: 0.9rem;
          }
        }
      }

      .detail-content {
        padding: 40px 24px;
        border-radius: 16px;
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

      /* Strategy Info Section */
      .strategy-info-section {
        padding: 32px;
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 32px;

        .model-info-header {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 16px;

          h3 {
            margin: 0;
            font-size: 1.6rem;
            font-weight: 600;
          }
        }

        .model-badge {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          background: var(--text-accent);
          color: white;
          padding: 6px 14px;
          border-radius: 30px;
          font-size: 0.85rem;
          font-weight: 600;

          mat-icon {
            font-size: 18px;
            width: 18px;
            height: 18px;
          }
        }

        .description {
          font-size: 1.05rem;
          color: var(--text-secondary);
          line-height: 1.6;
          margin-bottom: 24px;
          max-width: 800px;
        }

        .config-nudge-box {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 20px 24px;
          background: rgba(146, 98, 249, 0.05);
          border: 1px dashed rgba(146, 98, 249, 0.3);
          border-radius: 16px;

          .nudge-text {
            display: flex;
            align-items: center;
            gap: 12px;
            color: var(--text-primary);

            p {
              margin: 0;
              font-size: 0.95rem;
              font-style: italic;
            }
          }

          .config-btn {
            height: 44px;
            padding: 0 24px;
            font-weight: 600;
          }
        }
      }

      /* MT5 Subscription Section */
      .mt5-subscription-section {
        padding: 32px;
        margin-top: 32px;
        border-radius: 20px;
        background: rgba(0, 255, 136, 0.03);
        border: 1px solid rgba(0, 255, 136, 0.1);

        .subscription-header {
          display: flex;
          align-items: center;
          gap: 20px;
          margin-bottom: 24px;

          h3 {
            margin: 0;
            font-size: 1.5rem;
            color: #00ff88;
          }

          p {
            margin: 4px 0 0 0;
            color: var(--text-secondary);
          }

          .large-icon {
            font-size: 40px;
            width: 40px;
            height: 40px;
            color: #00ff88;
          }
        }

        .subscription-content {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
          align-items: end;

          .feature-item {
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--text-primary);

            mat-icon {
              color: #00ff88;
              font-size: 20px;
              width: 20px;
              height: 20px;
            }
          }

          .subscribe-btn {
            grid-column: 1 / -1;
            margin-top: 16px;
            height: 52px;
            font-size: 1.1rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            background: linear-gradient(90deg, #00ff88, #00ccff) !important;
            color: #000 !important;
            opacity: 0.8;
          }
        }
      }

      /* Premium Locked Section */
      .premium-locked-section {
        position: relative;
        transition: all 0.3s ease;

        &.locked {
          opacity: 0.4;
          filter: grayscale(0.5) blur(1px);
          pointer-events: none;
          user-select: none;
        }

        .premium-badge-overlay {
          position: absolute;
          top: 12px;
          right: 12px;
          z-index: 100;
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 8px 16px;
          background: rgba(0, 0, 0, 0.6);
          backdrop-filter: blur(8px);
          border: 1px solid rgba(255, 215, 0, 0.3);
          border-radius: 12px;
          color: #ffd700;
          font-weight: 600;
          font-size: 0.85rem;
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
          pointer-events: auto;

          mat-icon {
            font-size: 18px;
            width: 18px;
            height: 18px;
          }

          mat-slide-toggle {
            transform: scale(0.8);
          }
        }
      }
    `,
  ],
})
export class DashboardComponent implements OnInit {
  selectedTabIndex = 0;
  trainingParams: TrainingParams | null = null;
  lastSavedParams: TrainingParams | null = null;
  backtestResults: BacktestResults | null = null;
  selectedStrategy: Strategy | null = null;

  showParamsCard = false;
  isModelTrained = false;
  isEnsembleModelTrained = false;
  isViewOnly = false;
  user: User | null = null;

  constructor(
    private apiService: ApiService,
    private authService: AuthService,
    private snackBar: MatSnackBar
  ) {
    this.authService.user$.subscribe((user) => (this.user = user));
  }

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

    // Mark based on current tab
    if (this.selectedTabIndex === 1) {
      this.isEnsembleModelTrained = true;
    } else {
      this.isModelTrained = true;
    }
  }

  onBacktestComplete(results: BacktestResults) {
    this.backtestResults = results;
    this.snackBar.open("Backtest completed successfully!", "Close", {
      duration: 3000,
      panelClass: ["success-snackbar"],
    });
    // Results appear in the current tab
  }

  onStrategyBacktest(strategy: Strategy) {
    this.selectedStrategy = strategy;
    this.isViewOnly = true; // Strategies from this tab are view-only
    // For Top Strategies, we already have the backtest results in the strategy object
    this.backtestResults = strategy.backtest || null;
  }

  closeDetailView() {
    this.selectedStrategy = null;
    this.isViewOnly = false;
    this.backtestResults = null;
  }

  onTabChange(index: number) {
    // You can add logic here if needed when tabs change
  }

  getModelDisplayName(type: string | undefined): string {
    const map: { [key: string]: string } = {
      xgboost: "XGBoost",
      lightgbm: "LightGBM",
      rf: "Random Forest",
      ensemble: "Ensemble (Multi-Model)",
    };
    return map[type || ""] || "XGBoost";
  }

  get ensembleParams(): TrainingParams | null {
    if (!this.trainingParams) return null;
    return {
      ...this.trainingParams,
      model: {
        ...this.trainingParams.model,
        model_type: "ensemble",
      },
    };
  }

  logout() {
    this.authService.logout();
    this.snackBar.open("Logged out", "Close", { duration: 2000 });
  }
}
