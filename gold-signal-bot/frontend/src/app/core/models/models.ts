export interface TrainingParams {
  indicators: {
    rsi_period: number;
    macd_fast: number;
    macd_slow: number;
    macd_signal: number;
    bb_period: number;
    bb_std_dev: number;
    atr_period: number;
    ema_fast: number;
    ema_slow: number;
  };
  risk: {
    stop_loss_percent: number;
    take_profit_percent: number;
    prob_threshold: number;
    use_atr_stops: boolean;
    use_trend_filter: boolean;
  };
  model: {
    model_type: "xgboost" | "lightgbm" | "rf";
    n_estimators: number;
    max_depth: number;
    min_samples_split: number;
  };
  data: {
    csv_path?: string;
    training_period?: string;
  };
}

export interface BacktestParams {
  period_days: number;
  initial_capital?: number;
}

export interface JobStatus {
  status: "pending" | "running" | "completed" | "failed";
  progress: number;
  message: string;
  updated_at: string;
}

export interface TrainingResults {
  metadata: {
    [key: string]: string;
  };
  output: string;
  model_path: string;
  timestamp: string;
}

export interface Trade {
  timestamp: string;
  type: "BUY" | "SELL";
  entry_price: number;
  sl: number;
  tp: number;
  close_price: number | null;
  close_timestamp: string | null;
  close_reason: string | null;
  pips: number | null;
  status: "Open" | "Closed";
  confidence: number;
}

export interface BacktestMetrics {
  total_pips: number;
  total_trades: number;
  closed_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  avg_win: number;
  avg_loss: number;
  profit_factor: number;
}

export interface EquityPoint {
  timestamp: string;
  pips: number;
}

export interface BacktestResults {
  trades: Trade[];
  metrics: BacktestMetrics;
  equity_curve: EquityPoint[];
  output: string;
  timestamp: string;
}

export interface Config {
  indicators: {
    rsi_period: number;
    macd_fast: number;
    macd_slow: number;
    macd_signal: number;
    bb_period: number;
    bb_std_dev: number;
    atr_period: number;
    ema_fast: number;
    ema_slow: number;
  };
  risk: {
    stop_loss_percent: number;
    take_profit_percent: number;
    prob_threshold: number;
    use_atr_stops: boolean;
    use_trend_filter: boolean;
  };
  model: {
    model_type: "xgboost" | "lightgbm" | "rf";
    n_estimators: number;
    max_depth: number;
    min_samples_split: number;
  };
  data: {
    ticker: string;
    interval: string;
    training_period: string;
    mt5_csv_path: string;
  };
}

export interface DataFile {
  name: string;
  path: string;
  size: number;
  modified: string;
}

export interface Strategy {
  id: string;
  name: string;
  training: {
    params: TrainingParams;
    metadata: any;
    timestamp: string;
  };
  backtest: {
    metrics: any;
    timestamp: string;
  };
}
