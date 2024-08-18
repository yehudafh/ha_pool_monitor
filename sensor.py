from homeassistant.helpers.entity import Entity

async def async_setup_entry(hass, config_entry, async_add_entities):
    config = config_entry.data
    async_add_entities([
        PoolSensor(config, "free_chlorine"),
        PoolSensor(config, "total_chlorine"),
        PoolSensor(config, "combined_chlorine"),
        PoolSensor(config, "cya_level"),
        PoolSensor(config, "pool_recommendations"),
    ])

class PoolSensor(Entity):
    def __init__(self, config, sensor_type):
        self._name = f"Pool {sensor_type.replace('_', ' ').title()}"
        self._state = None
        self._config = config
        self._sensor_type = sensor_type

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        ph = float(self.hass.states.get(self._config["ph"]).state)
        temp = float(self.hass.states.get(self._config["temp"]).state)
        tds = float(self.hass.states.get(self._config["tds"]).state)
        ec = float(self.hass.states.get(self._config["ec"]).state)
        salinity = float(self.hass.states.get(self._config["salinity"]).state)
        orp = float(self.hass.states.get(self._config["orp"]).state)

        if self._sensor_type == "free_chlorine":
            self._state = round((orp - 500) * 0.01 - (ph - 7) * 0.05 + (temp - 25) * 0.02 + (salinity - 1000) * 0.001 - (tds - 1000) * 0.0005, 2)
        elif self._sensor_type == "total_chlorine":
            free_chlorine = float(self.hass.states.get(f"sensor.pool_free_chlorine").state)
            self._state = round(free_chlorine + 1.5, 2)
        elif self._sensor_type == "combined_chlorine":
            total_chlorine = float(self.hass.states.get(f"sensor.pool_total_chlorine").state)
            free_chlorine = float(self.hass.states.get(f"sensor.pool_free_chlorine").state)
            self._state = round(total_chlorine - free_chlorine, 2)
        elif self._sensor_type == "cya_level":
            orp_constant = 700
            cya_constant = 0.057
            temperature_factor = (temp - 25) * 0.02
            ph_factor = (ph - 7.5) * 0.03
            salinity_factor = (salinity - 1000) * 0.01
            tds_factor = (tds - 1000) * 0.005
            adjusted_orp = orp - (orp_constant + temperature_factor + ph_factor + salinity_factor + tds_factor)
            self._state = round(adjusted_orp / cya_constant, 0)
        elif self._sensor_type == "pool_recommendations":
            recommendations = []
            if free_chlorine < 1.5:
                chlorine_needed = round((1.5 - free_chlorine) * self._config["pool_volume"] * 0.5, 0)
                recommendations.append(f"הוסף {chlorine_needed} מ\"ל כלור")
            if ph < 7.2:
                acid_amount = round((7.2 - ph) * self._config["pool_volume"] * 0.1, 2)
                recommendations.append(f"הוסף {acid_amount} גרם סודה אש")
            elif ph > 7.8:
                soda_ash_amount = round((ph - 7.8) * self._config["pool_volume"] * 0.1, 2)
                recommendations.append(f"הוסף {soda_ash_amount} מ\"ל חומצת מלח")
            if cya > 50:
                recommendations.append("חומצה ציאנורית גבוהה מהטווח המומלץ")
            if salinity > 1300:
                recommendations.append("המליחות גבוהה מאוד (עולה על 1300 ppm)")
            elif salinity < 800:
                recommendations.append("המליחות נמוכה מאוד (מתחת ל-800 ppm)")
            if ph < 6.8:
                recommendations.append("ה-pH נמוך מאוד (מתחת ל-6.8)")
            elif ph > 8.0:
                recommendations.append("ה-pH גבוה מאוד (מעל ל-8.0)")
            if free_chlorine < 1.0:
                recommendations.append("רמת הכלור החופשי נמוכה מאוד (מתחת ל-1.0 ppm)")
            elif free_chlorine > 3.0:
                recommendations.append("רמת הכלור החופשי גבוהה מאוד (מעל ל-3.0 ppm)")
            if recommendations:
                self._state = ", ".join(recommendations)
            else:
                self._state = "-"
