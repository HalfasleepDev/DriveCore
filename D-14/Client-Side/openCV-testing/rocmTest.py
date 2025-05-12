import torch

print(torch.cuda.is_available())
print(torch.cuda.device_count())
print(torch.cuda.current_device())

print(torch.cuda.get_device_name(0))        # AMD Radeon RX 7700s