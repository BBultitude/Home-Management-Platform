import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { X, Plus } from 'lucide-react';
import { toast } from 'sonner';
import { knowledgeService, type ArticleType, type KnowledgeArticle } from '@/services/knowledgeService';
import { Checkbox } from '@/components/ui/checkbox';

type ArticleFormProps = Readonly<{
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  article?: KnowledgeArticle | null;
}>

const ARTICLE_TYPES: { value: ArticleType; label: string; description: string }[] = [
  { value: 'Measurement', label: 'Measurement', description: 'Room dimensions, window sizes, etc.' },
  { value: 'Paint', label: 'Paint', description: 'Paint colors and finishes used' },
  { value: 'TechDevice', label: 'Tech Device', description: 'WiFi routers, smart devices, etc.' },
  { value: 'StorageLocation', label: 'Storage Location', description: 'What is stored where' },
  { value: 'Vehicle', label: 'Vehicle', description: 'Cars, motorcycles, bicycles' },
  { value: 'EmergencyContact', label: 'Emergency Contact', description: 'Important contacts and services' },
  { value: 'Appliance', label: 'Appliance', description: 'Home appliances and equipment' },
  { value: 'Vendor', label: 'Vendor', description: 'Service providers and contractors' },
];

export const ArticleForm: React.FC<ArticleFormProps> = ({ open, onClose, onSuccess, article }) => {
  const [step, setStep] = useState<'type' | 'form'>(article ? 'form' : 'type');
  const [articleType, setArticleType] = useState<ArticleType | null>(article?.article_type || null);
  const [title, setTitle] = useState('');
  const [data, setData] = useState<Record<string, any>>({});
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState('');
  const [attachmentIds, setAttachmentIds] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (article) {
      setStep('form');
      setArticleType(article.article_type);
      setTitle(article.title);
      setData(article.data);
      setTags(article.tags);
    } else {
      setStep('type');
      setArticleType(null);
      setTitle('');
      setData({});
      setTags([]);
      setAttachmentIds([]);
    }
  }, [article, open]);

  const handleTypeSelect = (type: ArticleType) => {
    setArticleType(type);
    setStep('form');
    // Initialize data with default values based on type
    initializeDataForType(type);
  };

  const initializeDataForType = (type: ArticleType) => {
    switch (type) {
      case 'StorageLocation':
        setData({ items_stored: [] });
        break;
      case 'Vehicle':
        setData({ service_history: [], photos: [] });
        break;
      case 'Appliance':
        setData({ service_history: [] });
        break;
      case 'Vendor':
        setData({ services_performed: [] });
        break;
      default:
        setData({});
    }
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setTags([...tags, tagInput.trim()]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tag: string) => {
    setTags(tags.filter((t) => t !== tag));
  };

  const handleSubmit = async () => {
    if (!articleType || !title.trim()) {
      toast.error('Please fill in all required fields');
      return;
    }

    // Validate required fields based on article type
    const validationError = validateDataForType(articleType, data);
    if (validationError) {
      toast.error(validationError);
      return;
    }

    setLoading(true);
    try {
      if (article) {
        await knowledgeService.articles.update(article.id, {
          title,
          data,
          tags,
        });
        toast.success('Article updated successfully');
      } else {
        await knowledgeService.articles.create({
          article_type: articleType,
          title,
          data,
          tags,
          attachment_ids: attachmentIds.map(String),
        });
        toast.success('Article created successfully');
      }
      onSuccess();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to save article');
    } finally {
      setLoading(false);
    }
  };

  const validateMeasurement = (data: Record<string, any>): string | null =>
    (!data.location || !data.measurement_type || !data.value || !data.unit)
      ? 'Please fill in location, measurement type, value, and unit' : null;

  const validatePaint = (data: Record<string, any>): string | null =>
    (!data.room_area || !data.surface_type || !data.brand || !data.product_line || !data.color_name || !data.finish)
      ? 'Please fill in all required paint fields' : null;

  const validateTechDevice = (data: Record<string, any>): string | null =>
    (!data.device_type || !data.brand_model || !data.location)
      ? 'Please fill in device type, brand/model, and location' : null;

  const validateStorageLocation = (data: Record<string, any>): string | null =>
    (!data.storage_area || !data.items_stored || data.items_stored.length === 0 || !data.category)
      ? 'Please fill in storage area, items stored, and category' : null;

  const validateVehicle = (data: Record<string, any>): string | null =>
    (!data.vehicle_type || !data.make || !data.model || !data.year)
      ? 'Please fill in vehicle type, make, model, and year' : null;

  const validateEmergencyContact = (data: Record<string, any>): string | null =>
    (!data.name || !data.relationship_role || !data.primary_phone || !data.category)
      ? 'Please fill in name, relationship/role, phone, and category' : null;

  const validateAppliance = (data: Record<string, any>): string | null =>
    (!data.appliance_type || !data.brand || !data.location)
      ? 'Please fill in appliance type, brand, and location' : null;

  const validateVendor = (data: Record<string, any>): string | null =>
    (!data.business_name || !data.service_type || !data.phone)
      ? 'Please fill in business name, service type, and phone' : null;

  const validateDataForType = (type: ArticleType, data: Record<string, any>): string | null => {
    const validators: Partial<Record<ArticleType, (d: Record<string, any>) => string | null>> = {
      Measurement: validateMeasurement,
      Paint: validatePaint,
      TechDevice: validateTechDevice,
      StorageLocation: validateStorageLocation,
      Vehicle: validateVehicle,
      EmergencyContact: validateEmergencyContact,
      Appliance: validateAppliance,
      Vendor: validateVendor,
    };
    return validators[type]?.(data) ?? null;
  };

  const updateData = (key: string, value: any) => {
    setData({ ...data, [key]: value });
  };

  const renderTypeSpecificForm = () => {
    if (!articleType) return null;

    switch (articleType) {
      case 'Measurement':
        return renderMeasurementForm();
      case 'Paint':
        return renderPaintForm();
      case 'TechDevice':
        return renderTechDeviceForm();
      case 'StorageLocation':
        return renderStorageLocationForm();
      case 'Vehicle':
        return renderVehicleForm();
      case 'EmergencyContact':
        return renderEmergencyContactForm();
      case 'Appliance':
        return renderApplianceForm();
      case 'Vendor':
        return renderVendorForm();
      default:
        return null;
    }
  };

  const renderMeasurementForm = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="location">Location *</Label>
          <Input
            id="location"
            placeholder="e.g., Master Bedroom"
            value={data.location || ''}
            onChange={(e) => updateData('location', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="measurement_type">Measurement Type *</Label>
          <Input
            id="measurement_type"
            placeholder="e.g., Window Width"
            value={data.measurement_type || ''}
            onChange={(e) => updateData('measurement_type', e.target.value)}
          />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="value">Value *</Label>
          <Input
            id="value"
            type="number"
            step="0.01"
            placeholder="e.g., 120.5"
            value={data.value || ''}
            onChange={(e) => updateData('value', Number.parseFloat(e.target.value))}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="unit">Unit *</Label>
          <Select value={data.unit || ''} onValueChange={(value) => updateData('unit', value)}>
            <SelectTrigger>
              <SelectValue placeholder="Select unit" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="cm">Centimeters (cm)</SelectItem>
              <SelectItem value="m">Meters (m)</SelectItem>
              <SelectItem value="inches">Inches</SelectItem>
              <SelectItem value="feet">Feet</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="date_measured">Date Measured</Label>
        <Input
          id="date_measured"
          type="date"
          value={data.date_measured || ''}
          onChange={(e) => updateData('date_measured', e.target.value)}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="notes">Notes</Label>
        <Textarea
          id="notes"
          placeholder="Additional notes..."
          value={data.notes || ''}
          onChange={(e) => updateData('notes', e.target.value)}
        />
      </div>
    </div>
  );

  const renderPaintForm = () => (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="room_area">Room/Area *</Label>
        <Input
          id="room_area"
          placeholder="e.g., Living Room - North Wall"
          value={data.room_area || ''}
          onChange={(e) => updateData('room_area', e.target.value)}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="surface_type">Surface Type *</Label>
        <Select value={data.surface_type || ''} onValueChange={(value) => updateData('surface_type', value)}>
          <SelectTrigger>
            <SelectValue placeholder="Select surface type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="Wall">Wall</SelectItem>
            <SelectItem value="Ceiling">Ceiling</SelectItem>
            <SelectItem value="Trim">Trim</SelectItem>
            <SelectItem value="Door">Door</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="brand">Brand *</Label>
          <Input
            id="brand"
            placeholder="e.g., Benjamin Moore"
            value={data.brand || ''}
            onChange={(e) => updateData('brand', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="product_line">Product Line *</Label>
          <Input
            id="product_line"
            placeholder="e.g., Regal Select"
            value={data.product_line || ''}
            onChange={(e) => updateData('product_line', e.target.value)}
          />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="color_name">Color Name *</Label>
          <Input
            id="color_name"
            placeholder="e.g., Swiss Coffee"
            value={data.color_name || ''}
            onChange={(e) => updateData('color_name', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="color_code">Color Code</Label>
          <Input
            id="color_code"
            placeholder="e.g., #F5F5DC"
            value={data.color_code || ''}
            onChange={(e) => updateData('color_code', e.target.value)}
          />
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="finish">Finish *</Label>
        <Select value={data.finish || ''} onValueChange={(value) => updateData('finish', value)}>
          <SelectTrigger>
            <SelectValue placeholder="Select finish" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="Matte">Matte</SelectItem>
            <SelectItem value="Satin">Satin</SelectItem>
            <SelectItem value="SemiGloss">Semi-Gloss</SelectItem>
            <SelectItem value="Gloss">Gloss</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="retailer">Retailer</Label>
          <Input
            id="retailer"
            placeholder="e.g., Home Depot"
            value={data.retailer || ''}
            onChange={(e) => updateData('retailer', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="purchase_date">Purchase Date</Label>
          <Input
            id="purchase_date"
            type="date"
            value={data.purchase_date || ''}
            onChange={(e) => updateData('purchase_date', e.target.value)}
          />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="quantity_used">Quantity Used</Label>
          <Input
            id="quantity_used"
            placeholder="e.g., 2 gallons"
            value={data.quantity_used || ''}
            onChange={(e) => updateData('quantity_used', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="coverage_area">Coverage Area</Label>
          <Input
            id="coverage_area"
            placeholder="e.g., 400 sq ft"
            value={data.coverage_area || ''}
            onChange={(e) => updateData('coverage_area', e.target.value)}
          />
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="notes">Notes</Label>
        <Textarea
          id="notes"
          placeholder="Additional notes..."
          value={data.notes || ''}
          onChange={(e) => updateData('notes', e.target.value)}
        />
      </div>
    </div>
  );

  const renderTechDeviceForm = () => (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="device_type">Device Type *</Label>
        <Select value={data.device_type || ''} onValueChange={(value) => updateData('device_type', value)}>
          <SelectTrigger>
            <SelectValue placeholder="Select device type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="Router">Router</SelectItem>
            <SelectItem value="Modem">Modem</SelectItem>
            <SelectItem value="AccessPoint">Access Point</SelectItem>
            <SelectItem value="SmartDevice">Smart Device</SelectItem>
            <SelectItem value="Other">Other</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="brand_model">Brand/Model *</Label>
          <Input
            id="brand_model"
            placeholder="e.g., Netgear Nighthawk R7000"
            value={data.brand_model || ''}
            onChange={(e) => updateData('brand_model', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="location">Location *</Label>
          <Input
            id="location"
            placeholder="e.g., Living Room"
            value={data.location || ''}
            onChange={(e) => updateData('location', e.target.value)}
          />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="ip_address">IP Address</Label>
          <Input
            id="ip_address"
            placeholder="e.g., 192.168.1.1"
            value={data.ip_address || ''}
            onChange={(e) => updateData('ip_address', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="mac_address">MAC Address</Label>
          <Input
            id="mac_address"
            placeholder="e.g., 00:11:22:33:44:55"
            value={data.mac_address || ''}
            onChange={(e) => updateData('mac_address', e.target.value)}
          />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="wifi_ssid">WiFi SSID</Label>
          <Input
            id="wifi_ssid"
            placeholder="Network name"
            value={data.wifi_ssid || ''}
            onChange={(e) => updateData('wifi_ssid', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="wifi_password">WiFi Password</Label>
          <Input
            id="wifi_password"
            type="password"
            placeholder="Encrypted by backend"
            value={data.wifi_password || ''}
            onChange={(e) => updateData('wifi_password', e.target.value)}
          />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="admin_url">Admin URL</Label>
          <Input
            id="admin_url"
            placeholder="e.g., http://192.168.1.1"
            value={data.admin_url || ''}
            onChange={(e) => updateData('admin_url', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="admin_username">Admin Username</Label>
          <Input
            id="admin_username"
            placeholder="Admin login username"
            value={data.admin_username || ''}
            onChange={(e) => updateData('admin_username', e.target.value)}
          />
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="admin_password">Admin Password</Label>
        <Input
          id="admin_password"
          type="password"
          placeholder="Encrypted by backend"
          value={data.admin_password || ''}
          onChange={(e) => updateData('admin_password', e.target.value)}
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="purchase_date">Purchase Date</Label>
          <Input
            id="purchase_date"
            type="date"
            value={data.purchase_date || ''}
            onChange={(e) => updateData('purchase_date', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="warranty_expiry">Warranty Expiry</Label>
          <Input
            id="warranty_expiry"
            type="date"
            value={data.warranty_expiry || ''}
            onChange={(e) => updateData('warranty_expiry', e.target.value)}
          />
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="notes">Notes</Label>
        <Textarea
          id="notes"
          placeholder="Additional notes..."
          value={data.notes || ''}
          onChange={(e) => updateData('notes', e.target.value)}
        />
      </div>
    </div>
  );

  const renderStorageLocationForm = () => {
    const items = data.items_stored || [];

    const addItem = () => {
      const input = document.getElementById('new_item') as HTMLInputElement;
      if (input?.value.trim()) {
        updateData('items_stored', [...items, input.value.trim()]);
        input.value = '';
      }
    };

    const removeItem = (index: number) => {
      updateData('items_stored', items.filter((_: any, i: number) => i !== index));
    };

    return (
      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="storage_area">Storage Area *</Label>
          <Input
            id="storage_area"
            placeholder="e.g., Garage - Top Shelf Left"
            value={data.storage_area || ''}
            onChange={(e) => updateData('storage_area', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label>Items Stored *</Label>
          <div className="flex gap-2">
            <Input
              id="new_item"
              placeholder="Add item..."
              onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addItem(); } }}
            />
            <Button type="button" onClick={addItem} variant="outline">
              <Plus className="h-4 w-4" />
            </Button>
          </div>
          <div className="flex flex-wrap gap-2 mt-2">
            {items.map((item: string, index: number) => (
              <Badge key={`${item}-${index}`} variant="secondary">
                {item}
                <X
                  className="h-3 w-3 ml-1 cursor-pointer"
                  onClick={() => removeItem(index)}
                />
              </Badge>
            ))}
          </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="category">Category *</Label>
          <Select value={data.category || ''} onValueChange={(value) => updateData('category', value)}>
            <SelectTrigger>
              <SelectValue placeholder="Select category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Seasonal">Seasonal</SelectItem>
              <SelectItem value="Tools">Tools</SelectItem>
              <SelectItem value="Documents">Documents</SelectItem>
              <SelectItem value="Holiday">Holiday</SelectItem>
              <SelectItem value="Other">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="last_updated">Last Updated</Label>
          <Input
            id="last_updated"
            type="date"
            value={data.last_updated || ''}
            onChange={(e) => updateData('last_updated', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="notes">Notes</Label>
          <Textarea
            id="notes"
            placeholder="Additional notes..."
            value={data.notes || ''}
            onChange={(e) => updateData('notes', e.target.value)}
          />
        </div>
      </div>
    );
  };

  const renderVehicleForm = () => (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="vehicle_type">Vehicle Type *</Label>
        <Select value={data.vehicle_type || ''} onValueChange={(value) => updateData('vehicle_type', value)}>
          <SelectTrigger>
            <SelectValue placeholder="Select vehicle type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="Car">Car</SelectItem>
            <SelectItem value="Motorcycle">Motorcycle</SelectItem>
            <SelectItem value="Bicycle">Bicycle</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div className="space-y-2">
          <Label htmlFor="make">Make *</Label>
          <Input
            id="make"
            placeholder="e.g., Toyota"
            value={data.make || ''}
            onChange={(e) => updateData('make', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="model">Model *</Label>
          <Input
            id="model"
            placeholder="e.g., Camry"
            value={data.model || ''}
            onChange={(e) => updateData('model', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="year">Year *</Label>
          <Input
            id="year"
            type="number"
            placeholder="e.g., 2020"
            value={data.year || ''}
            onChange={(e) => updateData('year', Number.parseInt(e.target.value))}
          />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="vin">VIN</Label>
          <Input
            id="vin"
            placeholder="Vehicle Identification Number"
            value={data.vin || ''}
            onChange={(e) => updateData('vin', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="registration_number">Registration Number</Label>
          <Input
            id="registration_number"
            placeholder="License plate number"
            value={data.registration_number || ''}
            onChange={(e) => updateData('registration_number', e.target.value)}
          />
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="registration_expiry">Registration Expiry</Label>
        <Input
          id="registration_expiry"
          type="date"
          value={data.registration_expiry || ''}
          onChange={(e) => updateData('registration_expiry', e.target.value)}
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="next_service_due">Next Service Due</Label>
          <Input
            id="next_service_due"
            type="date"
            value={data.next_service_due || ''}
            onChange={(e) => updateData('next_service_due', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="next_service_km">Next Service (km/mi)</Label>
          <Input
            id="next_service_km"
            type="number"
            placeholder="e.g., 10000"
            value={data.next_service_km || ''}
            onChange={(e) => updateData('next_service_km', Number.parseInt(e.target.value))}
          />
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="notes">Notes</Label>
        <Textarea
          id="notes"
          placeholder="Additional notes..."
          value={data.notes || ''}
          onChange={(e) => updateData('notes', e.target.value)}
        />
      </div>
    </div>
  );

  const renderEmergencyContactForm = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="name">Name *</Label>
          <Input
            id="name"
            placeholder="Contact name"
            value={data.name || ''}
            onChange={(e) => updateData('name', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="relationship_role">Relationship/Role *</Label>
          <Input
            id="relationship_role"
            placeholder="e.g., Electrician, Family"
            value={data.relationship_role || ''}
            onChange={(e) => updateData('relationship_role', e.target.value)}
          />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="primary_phone">Primary Phone *</Label>
          <Input
            id="primary_phone"
            type="tel"
            placeholder="e.g., (555) 123-4567"
            value={data.primary_phone || ''}
            onChange={(e) => updateData('primary_phone', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="secondary_phone">Secondary Phone</Label>
          <Input
            id="secondary_phone"
            type="tel"
            placeholder="Alternative number"
            value={data.secondary_phone || ''}
            onChange={(e) => updateData('secondary_phone', e.target.value)}
          />
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          placeholder="email@example.com"
          value={data.email || ''}
          onChange={(e) => updateData('email', e.target.value)}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="address">Address</Label>
        <Input
          id="address"
          placeholder="Full address"
          value={data.address || ''}
          onChange={(e) => updateData('address', e.target.value)}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="category">Category *</Label>
        <Select value={data.category || ''} onValueChange={(value) => updateData('category', value)}>
          <SelectTrigger>
            <SelectValue placeholder="Select category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="Medical">Medical</SelectItem>
            <SelectItem value="Utilities">Utilities</SelectItem>
            <SelectItem value="Trades">Trades</SelectItem>
            <SelectItem value="Family">Family</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-2">
        <Label htmlFor="when_to_call">When to Call</Label>
        <Input
          id="when_to_call"
          placeholder="e.g., Power outage, Medical emergency"
          value={data.when_to_call || ''}
          onChange={(e) => updateData('when_to_call', e.target.value)}
        />
      </div>
      <div className="flex items-center space-x-2">
        <Checkbox
          id="pinned"
          checked={data.pinned || false}
          onCheckedChange={(checked) => updateData('pinned', checked)}
        />
        <Label htmlFor="pinned" className="cursor-pointer">
          Pin to dashboard for quick access
        </Label>
      </div>
      <div className="space-y-2">
        <Label htmlFor="notes">Notes</Label>
        <Textarea
          id="notes"
          placeholder="Additional notes..."
          value={data.notes || ''}
          onChange={(e) => updateData('notes', e.target.value)}
        />
      </div>
    </div>
  );

  const renderApplianceForm = () => (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="appliance_type">Appliance Type *</Label>
        <Select value={data.appliance_type || ''} onValueChange={(value) => updateData('appliance_type', value)}>
          <SelectTrigger>
            <SelectValue placeholder="Select appliance type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="Fridge">Fridge</SelectItem>
            <SelectItem value="Washer">Washer</SelectItem>
            <SelectItem value="Dryer">Dryer</SelectItem>
            <SelectItem value="HVAC">HVAC</SelectItem>
            <SelectItem value="Oven">Oven</SelectItem>
            <SelectItem value="Dishwasher">Dishwasher</SelectItem>
            <SelectItem value="Other">Other</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="brand">Brand *</Label>
          <Input
            id="brand"
            placeholder="e.g., Samsung"
            value={data.brand || ''}
            onChange={(e) => updateData('brand', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="location">Location *</Label>
          <Input
            id="location"
            placeholder="e.g., Kitchen"
            value={data.location || ''}
            onChange={(e) => updateData('location', e.target.value)}
          />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="model_number">Model Number</Label>
          <Input
            id="model_number"
            placeholder="Model number"
            value={data.model_number || ''}
            onChange={(e) => updateData('model_number', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="serial_number">Serial Number</Label>
          <Input
            id="serial_number"
            placeholder="Serial number"
            value={data.serial_number || ''}
            onChange={(e) => updateData('serial_number', e.target.value)}
          />
        </div>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div className="space-y-2">
          <Label htmlFor="purchase_date">Purchase Date</Label>
          <Input
            id="purchase_date"
            type="date"
            value={data.purchase_date || ''}
            onChange={(e) => updateData('purchase_date', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="purchase_price">Purchase Price</Label>
          <Input
            id="purchase_price"
            type="number"
            step="0.01"
            placeholder="0.00"
            value={data.purchase_price || ''}
            onChange={(e) => updateData('purchase_price', Number.parseFloat(e.target.value))}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="retailer">Retailer</Label>
          <Input
            id="retailer"
            placeholder="Where purchased"
            value={data.retailer || ''}
            onChange={(e) => updateData('retailer', e.target.value)}
          />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="warranty_expiry">Warranty Expiry</Label>
          <Input
            id="warranty_expiry"
            type="date"
            value={data.warranty_expiry || ''}
            onChange={(e) => updateData('warranty_expiry', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="energy_rating">Energy Rating</Label>
          <Input
            id="energy_rating"
            placeholder="e.g., A+++"
            value={data.energy_rating || ''}
            onChange={(e) => updateData('energy_rating', e.target.value)}
          />
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="notes">Notes</Label>
        <Textarea
          id="notes"
          placeholder="Additional notes..."
          value={data.notes || ''}
          onChange={(e) => updateData('notes', e.target.value)}
        />
      </div>
    </div>
  );

  const renderVendorForm = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="business_name">Business Name *</Label>
          <Input
            id="business_name"
            placeholder="Company name"
            value={data.business_name || ''}
            onChange={(e) => updateData('business_name', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="contact_person">Contact Person</Label>
          <Input
            id="contact_person"
            placeholder="Primary contact"
            value={data.contact_person || ''}
            onChange={(e) => updateData('contact_person', e.target.value)}
          />
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="service_type">Service Type *</Label>
        <Select value={data.service_type || ''} onValueChange={(value) => updateData('service_type', value)}>
          <SelectTrigger>
            <SelectValue placeholder="Select service type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="Electrician">Electrician</SelectItem>
            <SelectItem value="Plumber">Plumber</SelectItem>
            <SelectItem value="Landscaper">Landscaper</SelectItem>
            <SelectItem value="Roofer">Roofer</SelectItem>
            <SelectItem value="HVAC">HVAC</SelectItem>
            <SelectItem value="Painter">Painter</SelectItem>
            <SelectItem value="Carpenter">Carpenter</SelectItem>
            <SelectItem value="Other">Other</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="phone">Phone *</Label>
          <Input
            id="phone"
            type="tel"
            placeholder="(555) 123-4567"
            value={data.phone || ''}
            onChange={(e) => updateData('phone', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            placeholder="email@example.com"
            value={data.email || ''}
            onChange={(e) => updateData('email', e.target.value)}
          />
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="website">Website</Label>
        <Input
          id="website"
          placeholder="https://example.com"
          value={data.website || ''}
          onChange={(e) => updateData('website', e.target.value)}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="address">Address</Label>
        <Input
          id="address"
          placeholder="Business address"
          value={data.address || ''}
          onChange={(e) => updateData('address', e.target.value)}
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="rating">Rating (1-5)</Label>
          <Select
            value={data.rating?.toString() || ''}
            onValueChange={(value) => updateData('rating', Number.parseInt(value))}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select rating" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">⭐ 1 Star</SelectItem>
              <SelectItem value="2">⭐⭐ 2 Stars</SelectItem>
              <SelectItem value="3">⭐⭐⭐ 3 Stars</SelectItem>
              <SelectItem value="4">⭐⭐⭐⭐ 4 Stars</SelectItem>
              <SelectItem value="5">⭐⭐⭐⭐⭐ 5 Stars</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="last_used_date">Last Used</Label>
          <Input
            id="last_used_date"
            type="date"
            value={data.last_used_date || ''}
            onChange={(e) => updateData('last_used_date', e.target.value)}
          />
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="cost_range">Cost Range</Label>
        <Input
          id="cost_range"
          placeholder="e.g., $50-100/hr"
          value={data.cost_range || ''}
          onChange={(e) => updateData('cost_range', e.target.value)}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="recommended_by">Recommended By</Label>
        <Input
          id="recommended_by"
          placeholder="Who recommended this vendor"
          value={data.recommended_by || ''}
          onChange={(e) => updateData('recommended_by', e.target.value)}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="notes_review">Notes/Review</Label>
        <Textarea
          id="notes_review"
          placeholder="Your review and notes..."
          value={data.notes_review || ''}
          onChange={(e) => updateData('notes_review', e.target.value)}
        />
      </div>
    </div>
  );

  if (step === 'type') {
    return (
      <Dialog open={open} onOpenChange={onClose}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto bg-white dark:bg-white">
          <DialogHeader>
            <DialogTitle>Select Article Type</DialogTitle>
            <DialogDescription>
              Choose the type of knowledge article you want to create
            </DialogDescription>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-4 py-4">
            {ARTICLE_TYPES.map((type) => (
              <button
                key={type.value}
                type="button"
                className="border rounded-lg p-4 hover:border-primary hover:bg-gray-50 transition-colors text-left w-full"
                onClick={() => handleTypeSelect(type.value)}
              >
                <h3 className="font-semibold text-lg mb-2">{type.label}</h3>
                <p className="text-sm text-muted-foreground">{type.description}</p>
              </button>
            ))}
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  const submitButtonLabel = loading ? 'Saving...' : (article ? 'Update' : 'Create');

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto bg-white dark:bg-white">
        <DialogHeader>
          <DialogTitle>
            {article ? 'Edit Article' : 'Create Article'}
            {articleType && ` - ${ARTICLE_TYPES.find((t) => t.value === articleType)?.label}`}
          </DialogTitle>
          <DialogDescription>
            {article ? 'Update the article details below' : 'Fill in the details for your new knowledge article'}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          <div className="space-y-2">
            <Label htmlFor="title">Article Title *</Label>
            <Input
              id="title"
              placeholder="Enter a descriptive title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          {renderTypeSpecificForm()}

          <div className="space-y-2">
            <Label>Tags</Label>
            <div className="flex gap-2">
              <Input
                placeholder="Add tag..."
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAddTag(); } }}
              />
              <Button type="button" onClick={handleAddTag} variant="outline">
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex flex-wrap gap-2 mt-2">
              {tags.map((tag) => (
                <Badge key={tag} variant="secondary">
                  {tag}
                  <X
                    className="h-3 w-3 ml-1 cursor-pointer"
                    onClick={() => handleRemoveTag(tag)}
                  />
                </Badge>
              ))}
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={loading}>
            {submitButtonLabel}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
