## AdGuard

Currently I have moved to [AdGuard Home](https://adguard.com/en/adguard-home/overview.html) solution for DNS based AdBlocking. [Their software](https://github.com/AdguardTeam/AdGuardHome/wiki/Docker) can run also inside docker. The main advantages of AdGuard are:

* Less restrictive default ad guard rules - PiHole in default configuration did break login with Apple ID on mac os x and, there were small issues with android phone
* You can convert [uBlock](https://github.com/gorhill/uBlock/) rules into AdGuard rules
* Rules are just a regexp!
* It is much faster and uses less resources
* There is a nifty ui where you can define your own mapping for local ip(Like I want to all devices in my home see HomeAssistant instance under address https://home-assistant.here)
* Supports DNS over https!

## Old DNS Adblock solution

### PiHole & Cloudflare
Everybody is tracking you, Google, Russia(damn you Putin), China(damn you commies) and others. [PiHole](https://pi-hole.net/) is nice software that blocks Ads/Trackin site on the DNS level. Additionaly I have mapped on my router Google DNS like 8.8.8.8 to point to PiHole instance.

Also to increase security I also configured dns over https. Now everytime any device in my network hits Pihole dns server, it will use secure dns over https to resolve domain. [There is a nice tutorial how to do this](https://docs.pi-hole.net/guides/dns-over-https/) and this how my ansible configuration script looks like:


```yaml
- hosts: master
  become: yes
  handlers:
    - name: restart cloudflared
      become: yes
      service:
        name: cloudflared
        enabled: yes
        state: restarted
    - name: reload systemctl
      become: yes
      command: systemctl daemon-reload
  tasks:
    - name: Check if cloudflared already installed
      command: 'cloudflared -v'
      register: is_cloudflared_installed
      ignore_errors: True
    - name: Download cloudflared
      when: is_cloudflared_installed is failed
      get_url:
        url: https://bin.equinox.io/c/VdrWdbjqyF/cloudflared-stable-linux-amd64.deb
        dest: /tmp/cloudflared-stable-linux-amd64.deb
    - name: Install cloudflared
      when: is_cloudflared_installed is failed
      apt:
        deb: /tmp/cloudflared-stable-linux-amd64.deb
    - name: Ensure group "cloudflared" exists
      group:
        name: cloudflared
        state: present
    - name: Adding user cloudflared
      user:
        name: cloudflared
        group: cloudflared
        create_home: no
        shell: /usr/sbin/nologin
        append: yes
    - name: Create /etc/default/cloudflared
      template:
        src: ./etc/default/cloudflared.j2
        dest: /etc/default/cloudflared
        owner: cloudflared
        group: cloudflared
    - name: Change file ownership for /usr/local/bin/cloudflared
      file:
        path: /usr/local/bin/cloudflared
        owner: cloudflared
        group: cloudflared
    - name: Create cloudflared.service
      template:
        src: ./lib/systemd/system/cloudflared.service.j2
        dest: /lib/systemd/system/cloudflared.service
      notify:
        - reload systemctl
        - restart cloudflared
```