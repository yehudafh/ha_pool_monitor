from homeassistant.helpers.entity import Entity
from homeassistant.helpers.translation import async_get_translations

async def async_setup_entry(hass, config_entry, async_add_entities):
    config = config_entry.data
    translations = await async_get_translations(hass, hass.config.language, "sensor", "pool_monitor")
    async_add_entities([
        PoolSensor(config, "free_chlorine", translations),
        PoolSensor(config, "total_chlorine", translations),
        PoolSensor(config, "combined_chlorine", translations),
        PoolSensor(config, "cya_level", translations),
        PoolSensor(config, "pool_recommendations", translations),
    ])

class PoolSensor(Entity):
    def __init__(self, config, sensor_type, translations):
        self._name = translations.get(f"sensor.{sensor_type}", sensor_type.replace('_', ' ').title())
        self._state = None
        self._config = config
        self._sensor_type = sensor_type
        self._translations = translations

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
                recommendations.append(self._translations.get("sensor.recommendation_add_chlorine", "Add {chlorine_needed} ml of chlorine").format(chlorine_needed=chlorine_needed))
            if ph < 7.2:
                acid_amount = round((7.2 - ph) * self._config["pool_volume"] * 0.1, 2)
                recommendations.append(self._translations.get("sensor.recommendation_add_acid", "Add {acid_amount} grams of soda ash").format(acid_amount=acid_amount))
            elif ph > 7.8:
                soda_ash_amount = round((ph - 7.8) * self._config["pool_volume"] * 0.1, 2)
                recommendations.append(self._translations.get("sensor.recommendation_add_soda_ash", "Add {soda_ash_amount} ml of muriatic acid").format(soda_ash_amount=soda_ash_amount))
            if cya > 50:
                recommendations.append(self._translations.get("sensor.recommendation_high_cya", "Cyanuric acid level is above the recommended range"))
            if salinity > 1300:
                recommendations.append(self._translations.get("sensor.recommendation_high_salinity", "Salinity is very high (above 1300 ppm)"))
            elif salinity < 800:
                recommendations.append(self._translations.get("sensor.recommendation_low_salinity", "Salinity is very low (below 800 ppm)"))
            if ph < 6.8:
                recommendations.append(self._translations.get("sensor.recommendation_low_ph", "pH is very low (below 6.8)"))
            elif ph > 8.0:
                recommendations.append(self._translations.get("sensor.recommendation_high_ph", "pH is very high (above 8.0)"))
            if free_chlorine < 1.0:
                recommendations.append(self._translations.get("sensor.recommendation_low_free_chlorine", "Free chlorine level is very low (below 1.0 ppm)"))
            elif free_chlorine > 3.0:
                recommendations.append(self._translations.get("sensor.recommendation_high_free_chlorine", "Free chlorine level is very high (above 3.0 ppm)"))
            if recommendations:
                self._state = ", ".join(recommendations)
            else:
                self._state = "-"
