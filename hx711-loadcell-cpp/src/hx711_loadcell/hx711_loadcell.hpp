#pragma once

#include <memory>
#include <string>
#include <vector>

#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "viam/sdk/components/sensor/sensor.hpp"
#include "viam/sdk/resource/resource.hpp"

namespace viam {
namespace hx711_loadcell {

class HX711LoadCell : public viam::sdk::Sensor {
   public:
    HX711LoadCell(std::string name);
    ~HX711LoadCell();
    void reconfigure(viam::sdk::Dependencies deps, viam::sdk::ResourceConfig cfg) override;
    viam::sdk::AttributeMap get_readings(const viam::sdk::AttributeMap& extra) override;
    viam::sdk::AttributeMap do_command(const viam::sdk::AttributeMap& command) override;

    static std::shared_ptr<viam::sdk::ResourceRegistration> resource_registration();
    static std::shared_ptr<HX711LoadCell> create(std::string name);

   private:
    gpio_num_t dout_pin_;
    gpio_num_t sck_pin_;
    int gain_;
    int number_of_readings_;
    float tare_offset_;
    
    // HX711 specific methods
    void setup_hx711();
    int32_t read_raw();
    void tare();
    void wait_for_ready();
    void set_gain();
};

}  // namespace hx711_loadcell
}  // namespace viam 