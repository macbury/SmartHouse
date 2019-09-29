## PiHole & Cloudflare
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