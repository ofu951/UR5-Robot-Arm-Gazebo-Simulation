#!/bin/bash
# SSH ile GitHub'a push için setup scripti

echo "=========================================="
echo "SSH GitHub Setup"
echo "=========================================="

# Repository URL'ini al
read -p "GitHub repository URL'inizi girin (örnek: https://github.com/ofu951/ur5_workspace.git): " REPO_URL

# HTTPS URL'ini SSH URL'ine çevir
SSH_URL=$(echo "$REPO_URL" | sed 's|https://github.com/|git@github.com:|' | sed 's|\.git$||')

echo ""
echo "Remote URL'i SSH'a çeviriliyor..."
git remote set-url origin "${SSH_URL}.git"

echo ""
echo "Remote URL güncellendi:"
git remote -v

echo ""
echo "=========================================="
echo "SSH bağlantısını test edin:"
echo "=========================================="
echo "ssh -T git@github.com"
echo ""
echo "Eğer 'Hi ofu951! You've successfully authenticated...' mesajı görürseniz,"
echo "bağlantı başarılıdır. Sonra push yapabilirsiniz:"
echo ""
echo "git push -u origin main"
echo ""

