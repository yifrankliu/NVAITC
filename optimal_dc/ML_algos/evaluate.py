"""
Evaluation utilities: roll out trained policies and compute metrics.
"""

import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


def rollout_episode(
    agent,
    env,
    max_steps: int = 5761,
    deterministic: bool = True,
    verbose: bool = False,
) -> Dict[str, float]:
    """
    Run one episode and compute metrics.

    Args:
        agent: PPO or other algorithm
        env: FrontierEnv
        max_steps: max episode length
        deterministic: use greedy policy
        verbose: log step-by-step

    Returns:
        {
            'episode_return': cumulative reward,
            'episode_length': number of steps,
            'total_cooling_power_kW': mean facility power,
            'total_cooling_energy_kWh': daily energy consumption,
            'mean_inlet_temp': mean cool inlet temp,
            'max_inlet_temp': max inlet temp,
            'n_constraint_violations': steps where T > T_max,
            'constraint_violation_rate': % of steps with violations,
        }
    """
    obs, info = env.reset()
    done = False
    step = 0
    episode_return = 0.0

    # Track metrics
    power_kW_list = []
    inlet_temps = []
    violations = 0

    while not done and step < max_steps:
        action = agent.predict(obs, deterministic=deterministic)
        obs, reward, terminated, truncated, info = env.step(action.to_dict())
        done = terminated or truncated

        episode_return += reward
        step += 1

        # Extract facility power if available in info
        if "facility_power_W" in info:
            power_kW_list.append(info["facility_power_W"] / 1000.0)

        # Track inlet temperature (from obs or info)
        if "mean_inlet_temp_K" in info:
            inlet_K = info["mean_inlet_temp_K"]
            inlet_temps.append(inlet_K)
            # Check constraint (e.g., T_max = 313 K = 40°C)
            if inlet_K > 313:
                violations += 1

        if verbose and step % 100 == 0:
            logger.info(f"Step {step}/{max_steps}: reward={reward:.2f}, cumulative={episode_return:.2f}")

    # Compute summary metrics
    dt_s = 15  # FMU timestep
    dt_h = dt_s / 3600.0

    total_cooling_power_kW = np.mean(power_kW_list) if power_kW_list else 0.0
    total_cooling_energy_kWh = total_cooling_power_kW * step * dt_h

    mean_inlet_temp_K = np.mean(inlet_temps) if inlet_temps else 0.0
    max_inlet_temp_K = np.max(inlet_temps) if inlet_temps else 0.0

    constraint_violation_rate = violations / max(step, 1)

    metrics = {
        "episode_return": float(episode_return),
        "episode_length": int(step),
        "total_cooling_power_kW": float(total_cooling_power_kW),
        "total_cooling_energy_kWh": float(total_cooling_energy_kWh),
        "mean_inlet_temp_K": float(mean_inlet_temp_K),
        "mean_inlet_temp_C": float(mean_inlet_temp_K - 273.15),
        "max_inlet_temp_K": float(max_inlet_temp_K),
        "max_inlet_temp_C": float(max_inlet_temp_K - 273.15),
        "n_constraint_violations": int(violations),
        "constraint_violation_rate": float(constraint_violation_rate),
    }

    return metrics


def evaluate_policy(
    agent,
    env,
    n_episodes: int = 5,
    deterministic: bool = True,
    max_steps_per_episode: int = 5761,
) -> Dict[str, float]:
    """
    Evaluate policy over multiple episodes and aggregate metrics.

    Args:
        agent: trained algorithm
        env: FrontierEnv
        n_episodes: number of evaluation episodes
        deterministic: use greedy policy
        max_steps_per_episode: max steps per episode

    Returns:
        {
            'mean_return': mean episode return,
            'std_return': std of episode returns,
            'mean_energy_kWh': mean daily energy,
            'std_energy_kWh': std of daily energy,
            'mean_constraint_violation_rate': mean % of violating steps,
            'worst_case_violation_rate': max violation rate seen,
            'mean_max_temp_C': mean of max inlet temps across episodes,
            'episodes_completed': n_episodes,
        }
    """
    logger.info(f"Evaluating policy over {n_episodes} episodes")

    episode_metrics = []
    for ep in range(n_episodes):
        metrics = rollout_episode(
            agent,
            env,
            max_steps=max_steps_per_episode,
            deterministic=deterministic,
            verbose=(ep == 0),  # verbose on first episode
        )
        episode_metrics.append(metrics)
        logger.info(
            f"Episode {ep+1}/{n_episodes}: "
            f"energy={metrics['total_cooling_energy_kWh']:.0f} kWh, "
            f"violations={metrics['constraint_violation_rate']*100:.1f}%"
        )

    # Aggregate
    returns = np.array([m["episode_return"] for m in episode_metrics])
    energies = np.array([m["total_cooling_energy_kWh"] for m in episode_metrics])
    violations = np.array([m["constraint_violation_rate"] for m in episode_metrics])
    max_temps = np.array([m["max_inlet_temp_C"] for m in episode_metrics])

    summary = {
        "mean_return": float(returns.mean()),
        "std_return": float(returns.std()),
        "min_return": float(returns.min()),
        "max_return": float(returns.max()),
        "mean_energy_kWh": float(energies.mean()),
        "std_energy_kWh": float(energies.std()),
        "min_energy_kWh": float(energies.min()),
        "max_energy_kWh": float(energies.max()),
        "mean_constraint_violation_rate": float(violations.mean()),
        "worst_case_violation_rate": float(violations.max()),
        "mean_max_temp_C": float(max_temps.mean()),
        "episodes_completed": int(n_episodes),
    }

    return summary


def compare_policies(
    agents: Dict[str, object],
    env,
    n_episodes: int = 5,
    deterministic: bool = True,
) -> Dict[str, Dict[str, float]]:
    """
    Compare multiple policies.

    Args:
        agents: {"agent_name": agent_object, ...}
        env: environment
        n_episodes: eval episodes per agent
        deterministic: greedy policy

    Returns:
        {"agent_name": summary_metrics, ...}
    """
    results = {}
    for name, agent in agents.items():
        logger.info(f"\n{'='*60}")
        logger.info(f"Evaluating {name}")
        logger.info(f"{'='*60}")
        summary = evaluate_policy(agent, env, n_episodes=n_episodes, deterministic=deterministic)
        results[name] = summary
    return results


def print_comparison_table(results: Dict[str, Dict[str, float]]) -> None:
    """Print comparison table of multiple policies."""
    if not results:
        logger.warning("No results to display")
        return

    logger.info("\n" + "=" * 100)
    logger.info("POLICY COMPARISON")
    logger.info("=" * 100)

    # Header
    header = "Policy".ljust(20)
    metrics_to_show = [
        ("Energy (kWh)", "mean_energy_kWh"),
        ("Violations (%)", "mean_constraint_violation_rate"),
        ("Max Temp (°C)", "mean_max_temp_C"),
        ("Return", "mean_return"),
    ]
    for display_name, _ in metrics_to_show:
        header += display_name.rjust(18)
    logger.info(header)
    logger.info("-" * 100)

    # Rows
    for policy_name, metrics in results.items():
        row = policy_name.ljust(20)
        for display_name, metric_key in metrics_to_show:
            value = metrics.get(metric_key, 0.0)
            if "%" in display_name:
                row += f"{value*100:15.1f}%"
            elif "°C" in display_name or "K" in display_name or "kWh" in display_name:
                row += f"{value:17.1f}"
            else:
                row += f"{value:17.2f}"
        logger.info(row)

    logger.info("=" * 100 + "\n")
