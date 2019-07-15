Vagrant.configure(2) do |config|
  config.vm.box = "macbury/bionic64"
  config.vm.box_version = "1.07"

  config.ssh.forward_agent = true
  config.ssh.insert_key = false

  config.vm.network "forwarded_port", guest: 80, host: 7000
  config.vm.network "forwarded_port", guest: 443, host: 443

  config.vm.provider "virtualbox" do |v|
	  v.memory = 2524
	  v.cpus = 2
    v.gui = true
	end
end
