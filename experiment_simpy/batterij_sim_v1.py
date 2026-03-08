import simpy
from dataclasses import dataclass, field
from typing import Callable, List, Dict


@dataclass
class Battery:
    capacity_kwh: float
    max_charge_kw: float
    max_discharge_kw: float
    eta_charge: float = 0.95
    eta_discharge: float = 0.95
    soc_kwh: float = 0.0

    def charge(self, power_kw: float, dt_h: float) -> float:
        """
        Laadt de batterij.
        Input:
            power_kw = beschikbaar laadvermogen aan AC-zijde
        Returns:
            werkelijk opgenomen AC-vermogen in kW
        """
        power_kw = max(0.0, min(power_kw, self.max_charge_kw))

        # hoeveel energie kan er nog in de batterij opgeslagen worden?
        remaining_capacity_kwh = self.capacity_kwh - self.soc_kwh
        if remaining_capacity_kwh <= 0:
            return 0.0

        # AC-energie tijdens deze stap
        requested_energy_ac = power_kw * dt_h

        # door laadverlies komt minder in de batterij terecht
        stored_energy_kwh = requested_energy_ac * self.eta_charge

        if stored_energy_kwh <= remaining_capacity_kwh:
            self.soc_kwh += stored_energy_kwh
            return power_kw

        # batterij raakt vol binnen deze tijdstap
        actual_stored_kwh = remaining_capacity_kwh
        actual_energy_ac = actual_stored_kwh / self.eta_charge
        actual_power_kw = actual_energy_ac / dt_h

        self.soc_kwh = self.capacity_kwh
        return actual_power_kw

    def discharge(self, power_kw: float, dt_h: float) -> float:
        """
        Ontlaadt de batterij.
        Input:
            power_kw = gewenst AC-vermogen naar de belasting
        Returns:
            werkelijk geleverd AC-vermogen in kW
        """
        power_kw = max(0.0, min(power_kw, self.max_discharge_kw))

        if self.soc_kwh <= 0:
            return 0.0

        requested_energy_ac = power_kw * dt_h

        # Om AC-energie te leveren moet meer uit de batterij komen
        required_battery_energy = requested_energy_ac / self.eta_discharge

        if required_battery_energy <= self.soc_kwh:
            self.soc_kwh -= required_battery_energy
            return power_kw

        # batterij raakt leeg binnen deze stap
        actual_battery_energy = self.soc_kwh
        actual_energy_ac = actual_battery_energy * self.eta_discharge
        actual_power_kw = actual_energy_ac / dt_h

        self.soc_kwh = 0.0
        return actual_power_kw