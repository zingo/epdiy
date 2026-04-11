#pragma once
#include <ArduinoJson.h>

inline void parse_forecast_levels(const std::string& json_str, int* levels, int max_levels) {
  if (json_str.empty() || json_str == "unknown") return;
  
  DynamicJsonDocument doc(2048);
  DeserializationError error = deserializeJson(doc, json_str);
  if (error) {
    return;
  }
  
  JsonArray array = doc.as<JsonArray>();
  int count = 0;
  for (JsonObject item : array) {
    if (count >= max_levels) break;
    if (item.containsKey("level")) {
      levels[count] = item["level"].as<int>();
    } else if (item.containsKey("numeric_state")) {
      levels[count] = item["numeric_state"].as<int>();
    }
    count++;
  }
}
