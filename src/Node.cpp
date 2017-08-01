#include "Node.h"

namespace mr_box_peripheral_board {

void Node::begin() {
  config_.set_buffer(get_buffer());
  config_.validator_.set_node(*this);
  config_.reset();
  config_.load();

  Serial.begin(57600);

  MAX11210_begin();
  SPI.begin();
}

}  // namespace mr_box_peripheral_board
