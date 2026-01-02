import { Component, Input, Output, EventEmitter, OnInit } from "@angular/core";
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
import { MatSliderModule } from "@angular/material/slider";
import { MatSlideToggleModule } from "@angular/material/slide-toggle";
import { MatSelectModule } from "@angular/material/select";
import { MatButtonModule } from "@angular/material/button";
import { MatIconModule } from "@angular/material/icon";
import { MatDividerModule } from "@angular/material/divider";
import { MatTooltipModule } from "@angular/material/tooltip";
import { ApiService } from "../../core/services/api.service";
import { TrainingParams, DataFile } from "../../core/models/models";

@Component({
  selector: "app-parameters-form",
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatIconModule,
    MatDividerModule,
    MatSliderModule,
    MatSlideToggleModule,
    MatButtonModule,
    MatTooltipModule,
  ],
  templateUrl: "./parameters-form.component.html",
  styleUrls: ["./parameters-form.component.scss"],
})
export class ParametersFormComponent implements OnInit {
  @Input() initialParams: TrainingParams | null = null;
  @Output() paramsChange = new EventEmitter<TrainingParams>();

  parametersForm!: FormGroup;
  dataFiles: DataFile[] = [];
  loading = false;

  modelDescriptions = {
    xgboost:
      "XGBoost is the industry standard for financial time series. It is highly efficient, accurate, and prevents overfitting.",
    lightgbm:
      "LightGBM is a high-performance gradient boosting framework that is often faster and more memory-efficient than XGBoost.",
    rf: "Random Forest is a reliable bagging model that creates multiple decision trees. It is robust against overfitting but slower to train.",
  };

  get selectedModelDescription(): string {
    const type = this.parametersForm
      ?.get("n_estimators")
      ?.parent?.get("model_type")?.value;
    return (
      this.modelDescriptions[type as keyof typeof this.modelDescriptions] || ""
    );
  }

  get stop_loss_percent() {
    return this.parametersForm.get("stop_loss_percent")!;
  }

  get take_profit_percent() {
    return this.parametersForm.get("take_profit_percent")!;
  }

  get prob_threshold() {
    return this.parametersForm.get("prob_threshold")!;
  }

  constructor(private fb: FormBuilder, private apiService: ApiService) {}

  ngOnInit() {
    this.initializeForm();
    this.loadDataFiles();

    // Watch for form changes
    this.parametersForm.valueChanges.subscribe(() => {
      if (this.parametersForm.valid) {
        this.emitParams();
      }
    });
  }

  initializeForm() {
    const defaults = this.initialParams || this.getDefaultParams();

    this.parametersForm = this.fb.group({
      // Indicators
      rsi_period: [
        defaults.indicators.rsi_period,
        [Validators.required, Validators.min(5), Validators.max(30)],
      ],
      macd_fast: [
        defaults.indicators.macd_fast,
        [Validators.required, Validators.min(5), Validators.max(50)],
      ],
      macd_slow: [
        defaults.indicators.macd_slow,
        [Validators.required, Validators.min(10), Validators.max(100)],
      ],
      macd_signal: [
        defaults.indicators.macd_signal,
        [Validators.required, Validators.min(5), Validators.max(20)],
      ],
      bb_period: [
        defaults.indicators.bb_period,
        [Validators.required, Validators.min(10), Validators.max(50)],
      ],
      bb_std_dev: [
        defaults.indicators.bb_std_dev,
        [Validators.required, Validators.min(1), Validators.max(3)],
      ],
      atr_period: [
        defaults.indicators.atr_period,
        [Validators.required, Validators.min(5), Validators.max(30)],
      ],
      ema_fast: [
        defaults.indicators.ema_fast,
        [Validators.required, Validators.min(10), Validators.max(100)],
      ],
      ema_slow: [
        defaults.indicators.ema_slow,
        [Validators.required, Validators.min(50), Validators.max(300)],
      ],

      // Risk Management
      stop_loss_percent: [
        defaults.risk.stop_loss_percent * 100,
        [Validators.required, Validators.min(0.1), Validators.max(5)],
      ],
      take_profit_percent: [
        defaults.risk.take_profit_percent * 100,
        [Validators.required, Validators.min(0.1), Validators.max(10)],
      ],
      prob_threshold: [
        defaults.risk.prob_threshold,
        [Validators.required, Validators.min(0.5), Validators.max(0.95)],
      ],
      use_atr_stops: [defaults.risk.use_atr_stops],
      use_trend_filter: [defaults.risk.use_trend_filter],

      // Model Hyperparameters
      model_type: [defaults.model.model_type || "xgboost", Validators.required],
      n_estimators: [
        defaults.model.n_estimators,
        [Validators.required, Validators.min(50), Validators.max(500)],
      ],
      max_depth: [
        defaults.model.max_depth,
        [Validators.required, Validators.min(3), Validators.max(20)],
      ],
      min_samples_split: [
        defaults.model.min_samples_split,
        [Validators.required, Validators.min(2), Validators.max(20)],
      ],

      // Data Source
      csv_path: [defaults.data.csv_path || ""],
      training_period: [defaults.data.training_period || "1y"],
    });
  }

  loadDataFiles() {
    this.loading = true;
    this.apiService.getDataFiles().subscribe({
      next: (response) => {
        this.dataFiles = response.files;
        this.loading = false;
      },
      error: (error) => {
        console.error("Failed to load data files:", error);
        this.loading = false;
      },
    });
  }

  emitParams() {
    const formValue = this.parametersForm.value;

    const params: TrainingParams = {
      indicators: {
        rsi_period: formValue.rsi_period,
        macd_fast: formValue.macd_fast,
        macd_slow: formValue.macd_slow,
        macd_signal: formValue.macd_signal,
        bb_period: formValue.bb_period,
        bb_std_dev: formValue.bb_std_dev,
        atr_period: formValue.atr_period,
        ema_fast: formValue.ema_fast,
        ema_slow: formValue.ema_slow,
      },
      risk: {
        stop_loss_percent: formValue.stop_loss_percent / 100,
        take_profit_percent: formValue.take_profit_percent / 100,
        prob_threshold: formValue.prob_threshold,
        use_atr_stops: formValue.use_atr_stops,
        use_trend_filter: formValue.use_trend_filter,
      },
      model: {
        model_type: formValue.model_type,
        n_estimators: formValue.n_estimators,
        max_depth: formValue.max_depth,
        min_samples_split: formValue.min_samples_split,
      },
      data: {
        csv_path: formValue.csv_path,
        training_period: formValue.training_period,
      },
    };

    this.paramsChange.emit(params);
  }

  resetToDefaults() {
    this.parametersForm.reset(this.getDefaultParams());
  }

  private getDefaultParams(): any {
    return {
      indicators: {
        rsi_period: 14,
        macd_fast: 12,
        macd_slow: 26,
        macd_signal: 9,
        bb_period: 20,
        bb_std_dev: 2,
        atr_period: 14,
        ema_fast: 50,
        ema_slow: 200,
      },
      risk: {
        stop_loss_percent: 0.5,
        take_profit_percent: 1.0,
        prob_threshold: 0.5,
        use_atr_stops: false,
        use_trend_filter: false,
      },
      model: {
        model_type: "xgboost",
        n_estimators: 300,
        max_depth: 6,
        min_samples_split: 5,
      },
      data: {
        csv_path: "",
        training_period: "1y",
      },
    };
  }
}
