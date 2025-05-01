#include "hx711_loadcell.hpp"

#include <chrono>
#include <thread>

#include "viam/sdk/common/proto_type.hpp"
#include "viam/sdk/components/sensor/sensor.hpp"
#include "viam/sdk/resource/resource.hpp"

namespace viam {
namespace hx711_loadcell {

static const char* TAG = "HX711LoadCell";

HX711LoadCell::HX711LoadCell(std::string name) : Sensor(std::move(name)) {
    // Initialize with default values
    dout_pin_ = GPIO_NUM_5;
    sck_pin_ = GPIO_NUM_6;
    gain_ = 64;
    number_of_readings_ = 3;
    tare_offset_ = 0.0f;
}

HX711LoadCell::~HX711LoadCell() {
    // Cleanup GPIO
    gpio_reset_pin(dout_pin_);
    gpio_reset_pin(sck_pin_);
}

void HX711LoadCell::reconfigure(viam::sdk::Dependencies deps, viam::sdk::ResourceConfig cfg) {
    // Parse configuration
    auto attrs = cfg.attributes();
    if (attrs->has("doutPin")) {
        dout_pin_ = static_cast<gpio_num_t>(attrs->at("doutPin")->get<int>());
    }
    if (attrs->has("sckPin")) {
        sck_pin_ = static_cast<gpio_num_t>(attrs->at("sckPin")->get<int>());
    }
    if (attrs->has("gain")) {
        gain_ = attrs->at("gain")->get<int>();
    }
    if (attrs->has("numberOfReadings")) {
        number_of_readings_ = attrs->at("numberOfReadings")->get<int>();
    }
    if (attrs->has("tare_offset")) {
        tare_offset_ = attrs->at("tare_offset")->get<float>();
    }

    setup_hx711();
}

void HX711LoadCell::setup_hx711() {
    // Configure DOUT pin as input
    gpio_config_t io_conf = {};
    io_conf.intr_type = GPIO_INTR_DISABLE;
    io_conf.mode = GPIO_MODE_INPUT;
    io_conf.pin_bit_mask = (1ULL << dout_pin_);
    io_conf.pull_up_en = GPIO_PULLUP_ENABLE;
    io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    gpio_config(&io_conf);

    // Configure SCK pin as output
    io_conf.mode = GPIO_MODE_OUTPUT;
    io_conf.pin_bit_mask = (1ULL << sck_pin_);
    io_conf.pull_up_en = GPIO_PULLUP_DISABLE;
    io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    gpio_config(&io_conf);

    // Set SCK low initially
    gpio_set_level(sck_pin_, 0);

    // Wait for HX711 to be ready
    wait_for_ready();
    set_gain();
}

void HX711LoadCell::wait_for_ready() {
    while (gpio_get_level(dout_pin_) == 1) {
        vTaskDelay(pdMS_TO_TICKS(1));
    }
}

void HX711LoadCell::set_gain() {
    // Pulse SCK to set gain
    for (int i = 0; i < gain_; i++) {
        gpio_set_level(sck_pin_, 1);
        vTaskDelay(pdMS_TO_TICKS(1));
        gpio_set_level(sck_pin_, 0);
        vTaskDelay(pdMS_TO_TICKS(1));
    }
}

int32_t HX711LoadCell::read_raw() {
    wait_for_ready();

    int32_t value = 0;
    uint8_t data[3] = {0};

    // Read 24 bits of data
    for (int i = 0; i < 24; i++) {
        gpio_set_level(sck_pin_, 1);
        vTaskDelay(pdMS_TO_TICKS(1));
        
        if (gpio_get_level(dout_pin_)) {
            value |= (1 << (23 - i));
        }
        
        gpio_set_level(sck_pin_, 0);
        vTaskDelay(pdMS_TO_TICKS(1));
    }

    // Set gain for next reading
    set_gain();

    // Convert to signed 32-bit integer
    if (value & 0x800000) {
        value |= 0xFF000000;
    }

    return value;
}

void HX711LoadCell::tare() {
    int32_t sum = 0;
    for (int i = 0; i < number_of_readings_; i++) {
        sum += read_raw();
        vTaskDelay(pdMS_TO_TICKS(10));
    }
    tare_offset_ = static_cast<float>(sum) / number_of_readings_;
}

viam::sdk::AttributeMap HX711LoadCell::get_readings(const viam::sdk::AttributeMap& extra) {
    auto readings = std::make_shared<viam::sdk::ProtoType>();
    auto map = readings->mutable_proto_struct();

    std::vector<float> measures_kg;
    int32_t sum = 0;

    for (int i = 0; i < number_of_readings_; i++) {
        int32_t raw = read_raw();
        float kg = (raw - tare_offset_) / 8200.0f;  // Assuming 8200 ~ 1kg
        measures_kg.push_back(kg);
        sum += raw;
        vTaskDelay(pdMS_TO_TICKS(10));
    }

    float avg_kgs = sum / (number_of_readings_ * 8200.0f);

    // Add readings to the map
    map->mutable_fields()->insert({"doutPin", viam::sdk::ProtoType::from_value(static_cast<int>(dout_pin_))});
    map->mutable_fields()->insert({"sckPin", viam::sdk::ProtoType::from_value(static_cast<int>(sck_pin_))});
    map->mutable_fields()->insert({"gain", viam::sdk::ProtoType::from_value(gain_)});
    map->mutable_fields()->insert({"numberOfReadings", viam::sdk::ProtoType::from_value(number_of_readings_)});
    map->mutable_fields()->insert({"tare_offset", viam::sdk::ProtoType::from_value(tare_offset_)});
    map->mutable_fields()->insert({"weight", viam::sdk::ProtoType::from_value(avg_kgs)});

    return readings;
}

viam::sdk::AttributeMap HX711LoadCell::do_command(const viam::sdk::AttributeMap& command) {
    auto result = std::make_shared<viam::sdk::ProtoType>();
    auto map = result->mutable_proto_struct();

    for (const auto& [key, value] : command->fields()) {
        if (key == "tare") {
            tare();
            map->mutable_fields()->insert({key, viam::sdk::ProtoType::from_value(true)});
        } else {
            map->mutable_fields()->insert({key, viam::sdk::ProtoType::from_value(false)});
        }
    }

    return result;
}

std::shared_ptr<viam::sdk::ResourceRegistration> HX711LoadCell::resource_registration() {
    return viam::sdk::ResourceRegistration::create<HX711LoadCell>(
        "edss", "hx711-loadcell", "loadcell");
}

std::shared_ptr<HX711LoadCell> HX711LoadCell::create(std::string name) {
    return std::make_shared<HX711LoadCell>(std::move(name));
}

}  // namespace hx711_loadcell
}  // namespace viam 