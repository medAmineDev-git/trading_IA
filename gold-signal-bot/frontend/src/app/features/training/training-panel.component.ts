import { Component, Input, Output, EventEmitter } from "@angular/core";
import { CommonModule } from "@angular/common";
import { MatCardModule } from "@angular/material/card";
import { MatButtonModule } from "@angular/material/button";
import { MatProgressBarModule } from "@angular/material/progress-bar";
import { MatIconModule } from "@angular/material/icon";
import { MatSnackBar, MatSnackBarModule } from "@angular/material/snack-bar";
import { ApiService } from "../../core/services/api.service";
import {
  TrainingParams,
  TrainingResults,
  JobStatus,
} from "../../core/models/models";

@Component({
  selector: "app-training-panel",
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatProgressBarModule,
    MatIconModule,
    MatSnackBarModule,
  ],
  templateUrl: "./training-panel.component.html",
  styleUrls: ["./training-panel.component.scss"],
})
export class TrainingPanelComponent {
  @Input() params: TrainingParams | null = null;
  @Input() showTrainButton = true;
  @Output() trainingComplete = new EventEmitter<void>();

  isTraining = false;
  trainingProgress = 0;
  trainingStatus = "";
  trainingResults: TrainingResults | null = null;
  error: string | null = null;

  constructor(private apiService: ApiService, private snackBar: MatSnackBar) {}

  startTraining() {
    if (!this.params) {
      this.snackBar.open("Please configure parameters first", "Close", {
        duration: 3000,
      });
      return;
    }

    this.isTraining = true;
    this.trainingProgress = 0;
    this.trainingStatus = "Starting training...";
    this.error = null;
    this.trainingResults = null;

    this.apiService.startTraining(this.params).subscribe({
      next: (response) => {
        this.pollTrainingStatus(response.job_id);
      },
      error: (error) => {
        this.handleError(error);
      },
    });
  }

  private pollTrainingStatus(jobId: string) {
    this.apiService.pollTrainingStatus(jobId).subscribe({
      next: (status: JobStatus) => {
        this.trainingProgress = status.progress;
        this.trainingStatus = status.message;

        if (status.status === "completed") {
          this.loadTrainingResults(jobId);
        } else if (status.status === "failed") {
          this.handleError(new Error(status.message));
        }
      },
      error: (error) => {
        this.handleError(error);
      },
    });
  }

  private loadTrainingResults(jobId: string) {
    this.apiService.getTrainingResults(jobId).subscribe({
      next: (results) => {
        this.trainingResults = results;
        this.isTraining = false;
        this.trainingComplete.emit();
      },
      error: (error) => {
        this.handleError(error);
      },
    });
  }

  private handleError(error: any) {
    this.isTraining = false;
    this.error = error.message || "Training failed";
    this.snackBar.open(this.error || "An error occurred", "Close", {
      duration: 5000,
      panelClass: ["error-snackbar"],
    });
  }

  getModelMetrics(): any[] {
    if (!this.trainingResults || !this.trainingResults.metadata["Models"])
      return [];

    try {
      const modelsJson = this.trainingResults.metadata["Models"];
      const modelsObj = JSON.parse(modelsJson);
      return Object.values(modelsObj);
    } catch (e) {
      console.error("Error parsing model metrics:", e);
      return [];
    }
  }

  getModelDisplayName(): string {
    const type = this.params?.model?.model_type || "xgboost";
    const map: { [key: string]: string } = {
      xgboost: "XGBoost",
      lightgbm: "LightGBM",
      rf: "Random Forest",
      ensemble: "Multi-model",
    };
    return map[type] || "XGBoost";
  }
}
